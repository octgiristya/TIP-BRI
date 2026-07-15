import asyncio
import os
import sys

# Add parent dir to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, close_mongo_connection
from app.importers.excel_parser import import_excel_to_mongo

async def main():
    await connect_to_mongo()
    
    files = {
        "brand_protection": "resource/brand_protection.xlsx",
        "card_leak": "resource/card_leak.xlsx",
        "account_leak": "resource/account_leak.xlsx"
    }
    
    for collection, path in files.items():
        if os.path.exists(path):
            print(f"Importing {path} into {collection}...")
            result = await import_excel_to_mongo(path, collection)
            print(f"Result for {collection}: {result}")
        else:
            print(f"File not found: {path}")
            
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
