from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from app.services.dashboard_service import (
    get_brand_protection_kpis,
    get_card_leak_dashboard,
    get_account_leak_dashboard
)
from app.database import get_database

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def brand_protection_page(request: Request):
    # Brand protection is the default page
    kpis = await get_brand_protection_kpis()
    return templates.TemplateResponse("brand_protection.html", {"request": request, "kpis": kpis, "active_tab": "brand"})

@router.get("/card-leak")
async def card_leak_page(request: Request):
    dashboard = await get_card_leak_dashboard()
    return templates.TemplateResponse("card_leak.html", {"request": request, "dashboard": dashboard, "active_tab": "card"})

@router.get("/api/card-leak-data")
async def card_leak_data(request: Request, draw: int = 1, start: int = 0, length: int = 10, search_value: str = ""):
    db = get_database()
    col = db["card_leak"]
    
    query = {}
    if search_value:
        # Just simple text search across a few fields for demo
        # A real implementation might use a text index
        query = {"$or": [
            {"Card Number": {"$regex": search_value, "$options": "i"}},
            {"card_system": {"$regex": search_value, "$options": "i"}},
            {"Bank Name": {"$regex": search_value, "$options": "i"}}
        ]}
        
    total_records = await col.count_documents({})
    filtered_records = await col.count_documents(query)
    
    data = await col.find(query).skip(start).limit(length).to_list(length)
    
    # Clean up _id for json serialization
    for row in data:
        row["_id"] = str(row["_id"])
        
    return {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    }

@router.get("/account-leak")
async def account_leak_page(request: Request):
    dashboard = await get_account_leak_dashboard()
    return templates.TemplateResponse("account_leak.html", {"request": request, "dashboard": dashboard, "active_tab": "account"})

@router.get("/account-leak/domain/{domain}")
async def account_leak_domain_page(request: Request, domain: str):
    db = get_database()
    col = db["account_leak"]
    
    # Fetch top 100 for this domain as a simple view
    records = await col.find({"service_host": domain}).limit(100).to_list(100)
    for row in records:
        row["_id"] = str(row["_id"])
        
    return templates.TemplateResponse("domain_detail.html", {"request": request, "domain": domain, "records": records, "active_tab": "account"})
