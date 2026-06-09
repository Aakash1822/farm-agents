from langchain_openai import ChatOpenAI
from app.core.config import settings

class LLMService:
    """Abstraction layer for LLM providers"""
    
    @staticmethod
    def get_llm(provider: str = "openai", temperature: float = 0.2):
        if provider == "openai" and settings.OPENAI_API_KEY:
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=temperature,
                api_key=settings.OPENAI_API_KEY
            )
        else:
            raise ValueError(f"No valid LLM provider configured: {provider}")