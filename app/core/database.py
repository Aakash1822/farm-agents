import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None
    connected: bool = False

mongodb = MongoDB()

async def connect_to_mongo():
    if not settings.MONGODB_URI:
        logger.warning("MongoDB URI is not configured. Chat persistence is disabled.")
        return

    mongodb.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        socketTimeoutMS=5000,
    )
    mongodb.db = mongodb.client[settings.MONGODB_DB]

    try:
        await mongodb.client.admin.command("ping")
        await mongodb.db.chat_history.create_index(
            [("user_id", 1), ("session_id", 1), ("timestamp", -1)],
            background=True,
        )
        mongodb.connected = True
        logger.info("Connected to MongoDB and ensured indexes exist.")
    except Exception as exc:
        mongodb.connected = False
        if mongodb.client:
            mongodb.client.close()
        mongodb.client = None
        mongodb.db = None
        raise RuntimeError(
            f"Unable to connect to MongoDB at {settings.MONGODB_URI}. "
            "Check MONGODB_URI and ensure MongoDB is running."
        ) from exc

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        mongodb.connected = False

async def save_chat_message(user_id: str, session_id: str, message: str, role: str):
    if not mongodb.connected or mongodb.db is None:
        logger.warning("Skipping chat persistence because MongoDB is not connected.")
        return

    doc = {
        "user_id": user_id,
        "session_id": session_id,
        "message": message,
        "role": role,
        "timestamp": datetime.utcnow(),
    }
    await mongodb.db.chat_history.insert_one(doc)

async def get_chat_history(user_id: str, session_id: str, limit: int = 10) -> List[Dict]:
    if not mongodb.connected or mongodb.db is None:
        return []

    cursor = mongodb.db.chat_history.find(
        {"user_id": user_id, "session_id": session_id}
    ).sort("timestamp", -1).limit(limit)
    history = await cursor.to_list(length=limit)
    return list(reversed(history))


def is_mongo_connected() -> bool:
    return mongodb.connected
