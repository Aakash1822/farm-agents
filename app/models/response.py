from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class FarmerResponse(BaseModel):
    response: str
    session_id: str
    response_time_ms: int

class ChatMessage(BaseModel):
    message: str
    role: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    history: List[ChatMessage]