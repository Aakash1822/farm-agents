from pydantic import BaseModel, Field
from typing import Optional

class FarmerQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Farmer's question")
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Chat session identifier")
    language: str = Field("hi", description="Language code (hi/en)")
    location: Optional[dict] = Field(None, description="Farm location coordinates")
    api_key: Optional[str] = Field(None, description="Optional OpenAI API key for this request")