from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import redis
from typing import Dict, Any
import json

from database import get_redis


class RateLimitMiddleware:
    def __init__(self, app, calls: int = 100, period: int = 60):
        self.app = app
        self.calls = calls
        self.period = period
        self.redis = get_redis()
    
    async def __call__(self, scope: Dict[str, Any], receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Get client IP
            client_ip = request.client.host
            current_time = int(time.time())
            window_start = current_time - (current_time % self.period)
            
            # Redis key for rate limiting
            key = f"rate_limit:{client_ip}:{window_start}"
            
            try:
                # Get current count
                current_requests = self.redis.get(key)
                
                if current_requests is None:
                    # First request in this window
                    self.redis.setex(key, self.period, 1)
                else:
                    current_count = int(current_requests)
                    if current_count >= self.calls:
                        # Rate limit exceeded
                        response = JSONResponse(
                            status_code=429,
                            content={"detail": "Rate limit exceeded"}
                        )
                        await response(scope, receive, send)
                        return
                    
                    # Increment counter
                    self.redis.incr(key)
            
            except Exception:
                # If Redis is unavailable, allow request
                pass
        
        await self.app(scope, receive, send)


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope: Dict[str, Any], receive, send):
        if scope["type"] == "http":
            async def add_security_headers(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    
                    # Add security headers
                    headers.update({
                        b"x-content-type-options": b"nosniff",
                        b"x-frame-options": b"DENY",
                        b"x-xss-protection": b"1; mode=block",
                        b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                        b"content-security-policy": b"default-src 'self'",
                        b"referrer-policy": b"strict-origin-when-cross-origin"
                    })
                    
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, add_security_headers)
        else:
            await self.app(scope, receive, send)