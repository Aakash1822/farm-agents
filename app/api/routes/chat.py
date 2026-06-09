from fastapi import APIRouter, Depends, HTTPException
from typing import List
import time

from app.models.request import FarmerQuery
from app.models.response import FarmerResponse, ChatHistoryResponse
from app.core.agent import get_agent_response, get_agent_response_with_key
from app.core.database import get_chat_history, save_chat_message
from app.api.middleware.rate_limit import rate_limiter
from app.services.analytics import track_event

router = APIRouter()

@router.post("/ask", response_model=FarmerResponse)
async def ask_question(
    query: FarmerQuery,
    _=Depends(rate_limiter)
):
    start_time = time.time()
    
    await save_chat_message(
        user_id=query.user_id,
        session_id=query.session_id,
        message=query.query,
        role="user"
    )
    
    if query.api_key:
        response = await get_agent_response_with_key(
            api_key=query.api_key,
            query=query.query,
            user_id=query.user_id,
            session_id=query.session_id,
        )
    else:
        response = await get_agent_response(
            query=query.query,
            user_id=query.user_id,
            session_id=query.session_id,
        )
    
    await save_chat_message(
        user_id=query.user_id,
        session_id=query.session_id,
        message=response,
        role="assistant"
    )
    
    await track_event("query_completed", {
        "user_id": query.user_id,
        "response_time_ms": int((time.time() - start_time) * 1000)
    })
    
    return FarmerResponse(
        response=response,
        session_id=query.session_id,
        response_time_ms=int((time.time() - start_time) * 1000)
    )

@router.get("/history/{user_id}/{session_id}", response_model=ChatHistoryResponse)
async def get_history(user_id: str, session_id: str, limit: int = 20):
    """Get chat history for a session"""
    history = await get_chat_history(user_id, session_id, limit)
    return ChatHistoryResponse(history=history)