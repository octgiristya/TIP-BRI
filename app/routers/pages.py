from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from datetime import datetime
from bson import ObjectId
from app.services.dashboard_service import (
    get_brand_protection_kpis,
    get_card_leak_dashboard,
    get_account_leak_dashboard,
    get_date_filter
)
from app.database import get_database

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def resolve_time_filter(request: Request, time: str = None) -> str:
    if time:
        request.session["time_filter"] = time
        return time
    return request.session.get("time_filter", "7d")

@router.get("/")
async def brand_protection_page(request: Request, time: str = None):
    time_filter = resolve_time_filter(request, time)
    kpis = await get_brand_protection_kpis(time_filter)
    return templates.TemplateResponse("brand_protection.html", {"request": request, "kpis": kpis, "active_tab": "brand", "current_time_filter": time_filter})

@router.get("/brand-protection/detail")
async def brand_protection_detail_page(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = 50,
    search: str = "",
    resource: str = "",
    time: str = None
):
    time_filter = resolve_time_filter(request, time)
    db = get_database()
    col = db["brand_protection"]
    
    # Build query
    query = {}
    if search:
        query["$or"] = [
            {"Brand": {"$regex": search, "$options": "i"}},
            {"Source": {"$regex": search, "$options": "i"}},
            {"Full URL": {"$regex": search, "$options": "i"}},
            {"Progress": {"$regex": search, "$options": "i"}}
        ]
        
    if resource:
        query["Resource"] = resource
    
    # Merge time filter
    date_filter = await get_date_filter(col, time_filter, "Detection Date")
    if date_filter:
        query.update(date_filter)
        
    total_records = await col.count_documents(query)
    total_pages = (total_records + limit - 1) // limit
    
    # Handle page boundary
    if page > total_pages and total_pages > 0:
        page = total_pages
        
    skip = (page - 1) * limit
    
    records = await col.find(query).sort("Detection Date", -1).skip(skip).limit(limit).to_list(limit)
    
    for r in records:
        r["_id"] = str(r["_id"])
        
    return templates.TemplateResponse("brand_protection_detail.html", {
        "request": request,
        "records": records,
        "active_tab": "brand",
        "current_page": page,
        "total_pages": total_pages,
        "search": search,
        "resource": resource,
        "total_records": total_records,
        "current_time_filter": time_filter
    })

@router.get("/card-leak")
async def card_leak_page(request: Request, time: str = None):
    time_filter = resolve_time_filter(request, time)
    dashboard = await get_card_leak_dashboard(time_filter)
    return templates.TemplateResponse("card_leak.html", {"request": request, "dashboard": dashboard, "active_tab": "card", "current_time_filter": time_filter})

@router.get("/card-leak/detail")
async def card_leak_detail_page(request: Request, time: str = None):
    time_filter = resolve_time_filter(request, time)
    db = get_database()
    col = db["card_leak"]
    
    # Merge time filter
    query = {}
    date_filter = await get_date_filter(col, time_filter, "date_first_seen")
    if date_filter:
        query.update(date_filter)
        
    records = await col.find(query).sort("date_first_seen", -1).to_list(length=None)
    for r in records:
        r["_id"] = str(r["_id"])
    return templates.TemplateResponse("card_leak_detail.html", {"request": request, "records": records, "active_tab": "card", "current_time_filter": time_filter})

@router.get("/api/card-leak-data")
async def card_leak_data(request: Request, draw: int = 1, start: int = 0, length: int = 10, search_value: str = ""):
    db = get_database()
    col = db["card_leak"]
    
    query = {}
    if search_value:
        query = {"$or": [
            {"card_number": {"$regex": search_value, "$options": "i"}},
            {"card_system": {"$regex": search_value, "$options": "i"}},
            {"card_issuer": {"$regex": search_value, "$options": "i"}}
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
async def account_leak_page(request: Request, time: str = None):
    time_filter = resolve_time_filter(request, time)
    dashboard = await get_account_leak_dashboard(time_filter)
    return templates.TemplateResponse("account_leak.html", {"request": request, "dashboard": dashboard, "active_tab": "account", "current_time_filter": time_filter})

@router.get("/account-leak/domain/{domain}")
async def account_leak_domain_page(request: Request, domain: str, time: str = None):
    time_filter = resolve_time_filter(request, time)
    db = get_database()
    col = db["account_leak"]
    
    # Merge time filter
    query = {"service_host": domain}
    date_filter = await get_date_filter(col, time_filter, "date_first_seen")
    if date_filter:
        query.update(date_filter)
        
    records = await col.find(query).limit(100).to_list(100)
    for row in records:
        row["_id"] = str(row["_id"])
        
    return templates.TemplateResponse("domain_detail.html", {"request": request, "domain": domain, "records": records, "active_tab": "account", "current_time_filter": time_filter})

@router.post("/api/brand-protection/toggle-progress/{record_id}")
async def toggle_brand_protection_progress(record_id: str):
    db = get_database()
    col = db["brand_protection"]
    
    # Fetch current record
    record = await col.find_one({"_id": ObjectId(record_id)})
    if not record:
        return {"success": False, "message": "Record not found"}
        
    current_progress = record.get("Progress", "Active")
    new_progress = "Active" if current_progress == "Resolved" else "Resolved"
    
    update_data = {"Progress": new_progress}
    
    if new_progress == "Resolved":
        update_data["Resolved Date"] = datetime.utcnow()
    else:
        update_data["Resolved Date"] = None
        
    await col.update_one({"_id": ObjectId(record_id)}, {"$set": update_data})
    
    return {"success": True, "new_progress": new_progress}

@router.post("/api/card-leak/toggle-block/{record_id}")
async def toggle_card_leak_block(record_id: str):
    db = get_database()
    col = db["card_leak"]
    
    # Fetch current record
    record = await col.find_one({"_id": ObjectId(record_id)})
    if not record:
        return {"success": False, "message": "Record not found"}
        
    current_status = record.get("Blockir Status", "Not Blocked")
    
    # Check if currently blocked
    is_blocked = False
    if current_status and "block" in str(current_status).lower() and "not" not in str(current_status).lower():
        is_blocked = True
        
    new_status = "Not Blocked" if is_blocked else "Blocked"
    
    await col.update_one({"_id": ObjectId(record_id)}, {"$set": {"Blockir Status": new_status}})
    
    return {"success": True, "new_status": new_status}

@router.post("/api/account-leak/toggle-reset/{record_id}")
async def toggle_account_leak_reset(record_id: str):
    db = get_database()
    col = db["account_leak"]
    
    # Fetch current record
    record = await col.find_one({"_id": ObjectId(record_id)})
    if not record:
        return {"success": False, "message": "Record not found"}
        
    current_status = record.get("Reset Password Status", "Not Reset")
    
    # Check if currently reset
    is_reset = False
    if current_status and "reset" in str(current_status).lower() and "not" not in str(current_status).lower():
        is_reset = True
        
    new_status = "Not Reset" if is_reset else "Reset Done"
    
    await col.update_one({"_id": ObjectId(record_id)}, {"$set": {"Reset Password Status": new_status}})
    
    return {"success": True, "new_status": new_status}
