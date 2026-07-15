from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None

db = Database()

def get_database():
    return db.client[settings.mongo_database]

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(
        host=settings.mongo_host,
        port=settings.mongo_port,
        # uuidRepresentation="standard" is common, but we'll leave defaults unless needed
    )

async def close_mongo_connection():
    if db.client:
        db.client.close()
