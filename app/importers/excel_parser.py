import pandas as pd
from app.database import get_database

def sanitize_for_mongo(record):
    for k, v in record.items():
        if isinstance(v, int) and (v > 2**63 - 1 or v < -2**63):
            record[k] = str(v)
    return record

async def import_excel_to_mongo(file_path: str, collection_name: str, mode: str = "replace") -> dict:
    """
    Reads an Excel file, converts all columns to dicts, 
    detects datetimes automatically (handled by pandas), 
    drops the collection (if mode is replace), and inserts new records.
    Returns a dict with statistics.
    """
    try:
        # Read Excel
        df = pd.read_excel(file_path)
        
        # Replace NaN with None for MongoDB compatibility
        df = df.where(pd.notnull(df), None)

        # Convert to dictionary records
        records = df.to_dict(orient="records")
        
        # Sanitize huge integers that crash MongoDB
        records = [sanitize_for_mongo(r) for r in records]

        db = get_database()
        collection = db[collection_name]

        # Drop existing only if in replace mode
        if mode == "replace":
            await collection.drop()

        if records:
            # Insert new
            result = await collection.insert_many(records)
            inserted_count = len(result.inserted_ids)
        else:
            inserted_count = 0

        return {
            "success": True,
            "inserted_count": inserted_count,
            "failed_count": 0,
            "message": "Import successful"
        }
    except Exception as e:
        return {
            "success": False,
            "inserted_count": 0,
            "failed_count": 0,
            "message": str(e)
        }
