import pandas as pd
import math
from app.database import get_database

async def import_excel_to_mongo(file_path: str, collection_name: str) -> dict:
    """
    Reads an Excel file, converts all columns to dicts, 
    detects datetimes automatically (handled by pandas), 
    drops the collection, and inserts new records.
    Returns a dict with statistics.
    """
    try:
        # Read Excel
        df = pd.read_excel(file_path)
        
        # Replace NaN with None for MongoDB compatibility
        df = df.where(pd.notnull(df), None)

        # Convert to dictionary records
        records = df.to_dict(orient="records")

        db = get_database()
        collection = db[collection_name]

        # Drop existing
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
