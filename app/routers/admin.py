import os
import time
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import verify_totp, settings
from app.importers.excel_parser import import_excel_to_mongo

router = APIRouter(prefix="/godcia")
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def admin_dashboard(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/godcia/login")
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/login")
async def login_page(request: Request):
    if request.session.get("is_admin"):
        return RedirectResponse(url="/godcia/")
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/login")
async def login_post(request: Request, totp: str = Form(...)):
    if verify_totp(settings.totp_secret, totp):
        request.session["is_admin"] = True
        return RedirectResponse(url="/godcia/", status_code=302)
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid TOTP"})

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@router.post("/upload")
async def upload_file(request: Request, collection: str = Form(...), file: UploadFile = File(...)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/godcia/login")
        
    allowed_collections = ["brand_protection", "card_leak", "account_leak"]
    if collection not in allowed_collections:
        return {"success": False, "message": "Invalid collection"}

    if not file.filename.endswith(('.xls', '.xlsx')):
        return {"success": False, "message": "Only Excel files are allowed"}

    # Save file temporarily
    os.makedirs(settings.upload_path, exist_ok=True)
    file_path = os.path.join(settings.upload_path, f"{collection}_{int(time.time())}.xlsx")
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    # Process file
    result = await import_excel_to_mongo(file_path, collection)
    
    # Store history (Bonus feature)
    from app.database import get_database
    db = get_database()
    history_col = db["import_history"]
    await history_col.insert_one({
        "timestamp": time.time(),
        "collection": collection,
        "filename": file.filename,
        "inserted_count": result["inserted_count"],
        "success": result["success"],
        "message": result["message"]
    })
    
    return result

@router.get("/history")
async def upload_history(request: Request):
    if not request.session.get("is_admin"):
        return {"error": "Unauthorized"}
        
    from app.database import get_database
    db = get_database()
    history = await db["import_history"].find().sort("timestamp", -1).limit(50).to_list(50)
    
    for h in history:
        h["_id"] = str(h["_id"])
        
    return {"history": history}
