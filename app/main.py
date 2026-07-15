from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import pages, admin

settings = get_settings()

app = FastAPI(title="CIA Threat Intelligence Dashboard")

# Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_key,
    max_age=3600 * 24
)

# Events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Custom Error Handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("error.html", {"request": request, "status_code": 404, "message": "Page Not Found"}, status_code=404)
    if exc.status_code == 500:
        return templates.TemplateResponse("error.html", {"request": request, "status_code": 500, "message": "Internal Server Error"}, status_code=500)
    return templates.TemplateResponse("error.html", {"request": request, "status_code": exc.status_code, "message": exc.detail}, status_code=exc.status_code)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("error.html", {"request": request, "status_code": 500, "message": "Internal Server Error"}, status_code=500)

# Include Routers
app.include_router(pages.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
