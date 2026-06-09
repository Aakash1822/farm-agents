from fastapi import APIRouter
from datetime import datetime

from app.core.database import is_mongo_connected

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check():
    return {
        "status": "ready",
        "mongodb": "connected" if is_mongo_connected() else "disconnected"
    }
