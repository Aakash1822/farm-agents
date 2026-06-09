from typing import Callable, Any
from functools import wraps
import asyncio
import time

def tool_with_retry(max_retries: int = 3):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        return f"Service unavailable. Please try later. Error: {str(e)}"
                    await asyncio.sleep(2 ** attempt)
            return "Service temporarily unavailable."
        return wrapper
    return decorator