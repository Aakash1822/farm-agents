from fastapi import Request, HTTPException
from collections import defaultdict
import time
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        self.requests_per_minute = settings.RATE_LIMIT_PER_MINUTE
        self.user_requests = defaultdict(list)
    
    async def __call__(self, request: Request):
        user_id = request.headers.get("X-User-ID", "anonymous")
        now = time.time()
        minute_ago = now - 60
        
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id] 
            if req_time > minute_ago
        ]
        
        if len(self.user_requests[user_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute."
            )
        
        self.user_requests[user_id].append(now)

rate_limiter = RateLimiter()