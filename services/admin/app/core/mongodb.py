"""MongoDB connection for audit logs."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings


settings = get_settings()

# MongoDB client
mongodb_client: AsyncIOMotorClient = None
mongodb_database: AsyncIOMotorDatabase = None


async def get_mongodb() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance.

    Returns:
        AsyncIOMotorDatabase: MongoDB database
    """
    global mongodb_client, mongodb_database

    if mongodb_database is None:
        mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb_database = mongodb_client[settings.mongodb_database]

    return mongodb_database


async def close_mongodb():
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
