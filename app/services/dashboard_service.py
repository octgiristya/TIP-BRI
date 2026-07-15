from app.database import get_database
from datetime import datetime, timedelta

async def get_brand_protection_kpis(start_date=None, end_date=None):
    db = get_database()
    col = db["brand_protection"]
    
    # We will aggregate to find totals by Resource and Progress
    pipeline = [
        {"$group": {
            "_id": {
                "resource": "$Resource",
                "is_resolved": {"$eq": ["$Progress", "Resolve"]}
            },
            "count": {"$sum": 1}
        }}
    ]
    
    results = await col.aggregate(pipeline).to_list(length=None)
    
    kpis = {
        "Website": {"total": 0, "resolved": 0, "not_resolved": 0},
        "Document": {"total": 0, "resolved": 0, "not_resolved": 0},
        "Social Media": {"total": 0, "resolved": 0, "not_resolved": 0},
        "Instant Messenger": {"total": 0, "resolved": 0, "not_resolved": 0},
    }
    
    for r in results:
        res_type = r["_id"]["resource"]
        is_resolved = r["_id"]["is_resolved"]
        count = r["count"]
        
        if res_type in kpis:
            kpis[res_type]["total"] += count
            if is_resolved:
                kpis[res_type]["resolved"] += count
            else:
                kpis[res_type]["not_resolved"] += count
                
    return kpis

async def get_card_leak_dashboard(start_date=None, end_date=None):
    db = get_database()
    col = db["card_leak"]
    
    total = await col.count_documents({})
    
    # Donut card_system
    pipeline_system = [
        {"$group": {"_id": "$card_system", "count": {"$sum": 1}}}
    ]
    sys_results = await col.aggregate(pipeline_system).to_list(length=None)
    card_systems = {r["_id"]: r["count"] for r in sys_results if r["_id"]}
    
    # Donut Validation
    pipeline_val = [
        {"$group": {"_id": "$Validation", "count": {"$sum": 1}}}
    ]
    val_results = await col.aggregate(pipeline_val).to_list(length=None)
    
    valid_count = 0
    invalid_count = 0
    for r in val_results:
        val = r["_id"]
        # Treat empty (None, "", NaN) as Valid
        if not val or val == "" or (isinstance(val, float) and val != val):
            valid_count += r["count"]
        elif str(val).lower() == "valid":
            valid_count += r["count"]
        else:
            invalid_count += r["count"]
            
    # Blockir Status
    pipeline_block = [
        {"$group": {"_id": "$Blockir Status", "count": {"$sum": 1}}}
    ]
    block_results = await col.aggregate(pipeline_block).to_list(length=None)
    blocked_count = 0
    not_blocked_count = 0
    
    for r in block_results:
        b = str(r["_id"]).lower() if r["_id"] else ""
        if "blocked" in b and "not" not in b:
            blocked_count += r["count"]
        elif b == "block":
            blocked_count += r["count"]
        else:
            not_blocked_count += r["count"]

    return {
        "total": total,
        "card_systems": card_systems,
        "validation": {"valid": valid_count, "invalid": invalid_count},
        "blockir": {"blocked": blocked_count, "not_blocked": not_blocked_count}
    }

async def get_account_leak_dashboard(start_date=None, end_date=None):
    db = get_database()
    col = db["account_leak"]
    
    total = await col.count_documents({})
    
    # Validation
    pipeline_val = [
        {"$group": {"_id": "$Validation", "count": {"$sum": 1}}}
    ]
    val_results = await col.aggregate(pipeline_val).to_list(length=None)
    valid_count = 0
    invalid_count = 0
    for r in val_results:
        val = r["_id"]
        if not val or val == "" or (isinstance(val, float) and val != val):
            valid_count += r["count"]
        elif str(val).lower() == "valid":
            valid_count += r["count"]
        else:
            invalid_count += r["count"]
            
    # Reset Password Status
    pipeline_reset = [
        {"$group": {"_id": "$Reset Password Status", "count": {"$sum": 1}}}
    ]
    reset_results = await col.aggregate(pipeline_reset).to_list(length=None)
    reset_count = 0
    not_reset_count = 0
    
    for r in reset_results:
        val = r["_id"]
        if not val or val == "" or (isinstance(val, float) and val != val):
            not_reset_count += r["count"]
        elif "not" in str(val).lower():
            not_reset_count += r["count"]
        else:
            reset_count += r["count"]
            
    # Domain Summary Table
    pipeline_domain = [
        {"$group": {
            "_id": "$service_host",
            "pic_team": {"$first": "$PIC Team"},
            "total": {"$sum": 1},
            "reset_count": {
                "$sum": {
                    "$cond": [
                        {"$and": [
                            {"$ne": ["$Reset Password Status", None]},
                            {"$ne": ["$Reset Password Status", ""]},
                            {"$regexMatch": {"input": {"$toString": "$Reset Password Status"}, "regex": ".*Reset.*", "options": "i"}},
                            {"$not": {"$regexMatch": {"input": {"$toString": "$Reset Password Status"}, "regex": ".*Not.*", "options": "i"}}}
                        ]},
                        1,
                        0
                    ]
                }
            }
        }},
        {"$sort": {"total": -1}}
    ]
    
    domain_results = await col.aggregate(pipeline_domain).to_list(length=100) # Limit 100 for summary
    
    domains = []
    for r in domain_results:
        d_total = r["total"]
        d_reset = r["reset_count"]
        d_not_reset = d_total - d_reset
        domains.append({
            "domain": r["_id"],
            "pic_team": r["pic_team"] if r["pic_team"] else "Unknown",
            "total": d_total,
            "reset": d_reset,
            "not_reset": d_not_reset
        })

    return {
        "total": total,
        "validation": {"valid": valid_count, "invalid": invalid_count},
        "reset_status": {"reset": reset_count, "not_reset": not_reset_count},
        "domains": domains
    }
