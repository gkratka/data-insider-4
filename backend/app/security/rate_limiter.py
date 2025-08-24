"""
Advanced rate limiting for API endpoints
"""
import time
import redis
import hashlib
import logging
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException
from functools import wraps

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter with sliding window algorithm"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    def check_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int,
        identifier: str = None
    ) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limit
        
        Args:
            key: Rate limit key (e.g., "login", "upload")
            limit: Number of requests allowed
            window: Time window in seconds
            identifier: Request identifier (IP, user ID, etc.)
            
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        if not identifier:
            identifier = "anonymous"
            
        rate_key = f"rate_limit:{key}:{identifier}"
        current_time = int(time.time())
        
        try:
            # Get current request count in the window
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(rate_key, 0, current_time - window)
            
            # Count requests in current window
            pipe.zcard(rate_key)
            
            # Add current request
            pipe.zadd(rate_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(rate_key, window)
            
            results = pipe.execute()
            
            current_requests = results[1]  # Count after cleanup
            
            # Check if limit exceeded
            is_allowed = current_requests < limit
            
            # Calculate reset time
            oldest_request_time = current_time - window + 1
            reset_time = oldest_request_time + window
            
            return is_allowed, {
                "limit": limit,
                "remaining": max(0, limit - current_requests - 1),
                "reset_time": reset_time,
                "retry_after": None if is_allowed else window,
                "requests_count": current_requests + 1
            }
            
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            # Fail open - allow request if Redis is down
            return True, {
                "limit": limit,
                "remaining": limit - 1,
                "reset_time": current_time + window,
                "requests_count": 1,
                "error": "Rate limiter unavailable"
            }
    
    def get_client_identifier(self, request: Request) -> str:
        """Extract client identifier from request"""
        # Try to get user ID from token
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"
            
        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
            
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # Fall back to direct client IP
        if hasattr(request, 'client') and request.client:
            return request.client.host
            
        return "unknown"
    
    def create_rate_limit_key(self, endpoint: str, method: str = None) -> str:
        """Create a consistent rate limit key"""
        if method:
            return f"{method.upper()}:{endpoint}"
        return endpoint


# Rate limiting configurations
RATE_LIMITS = {
    "login": {"limit": 5, "window": 300},  # 5 attempts per 5 minutes
    "upload": {"limit": 10, "window": 60},  # 10 uploads per minute
    "chat": {"limit": 30, "window": 60},   # 30 messages per minute
    "api_key": {"limit": 1000, "window": 3600},  # 1000 requests per hour
    "general": {"limit": 100, "window": 60},  # 100 requests per minute
}


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, redis_url: str = "redis://localhost:6379"):
        self.app = app
        self.rate_limiter = RateLimiter(redis_url)
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limiting(request.url.path):
            await self.app(scope, receive, send)
            return
            
        # Determine rate limit type
        rate_limit_key = self._get_rate_limit_key(request)
        config = RATE_LIMITS.get(rate_limit_key, RATE_LIMITS["general"])
        
        # Check rate limit
        identifier = self.rate_limiter.get_client_identifier(request)
        is_allowed, info = self.rate_limiter.check_rate_limit(
            rate_limit_key,
            config["limit"],
            config["window"],
            identifier
        )
        
        if not is_allowed:
            # Rate limit exceeded
            response = {
                "detail": "Rate limit exceeded",
                "rate_limit_info": info
            }
            
            headers = {
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_time"]),
                "Retry-After": str(info["retry_after"]) if info["retry_after"] else "60"
            }
            
            # Send rate limit response
            response_body = b'{"detail":"Rate limit exceeded"}'
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [[k.encode(), v.encode()] for k, v in headers.items()],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
            return
        
        # Add rate limit headers to response
        def add_rate_limit_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers.update({
                    b"X-RateLimit-Limit": str(info["limit"]).encode(),
                    b"X-RateLimit-Remaining": str(info["remaining"]).encode(),
                    b"X-RateLimit-Reset": str(info["reset_time"]).encode(),
                })
                message["headers"] = list(headers.items())
            return message
            
        # Continue with request
        await self.app(scope, receive, lambda message: send(add_rate_limit_headers(message)))
    
    def _should_skip_rate_limiting(self, path: str) -> bool:
        """Determine if path should skip rate limiting"""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Determine rate limit key based on request"""
        path = request.url.path
        method = request.method
        
        # Specific endpoint mappings
        if "/auth/token" in path:
            return "login"
        elif "/files/upload" in path:
            return "upload"
        elif "/chat/" in path:
            return "chat"
        elif request.headers.get("X-API-Key"):
            return "api_key"
        else:
            return "general"


def rate_limit(key: str = None, limit: int = None, window: int = None):
    """
    Decorator for rate limiting specific endpoints
    
    Usage:
        @rate_limit("login", limit=5, window=300)
        async def login_endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Use provided config or defaults
            rate_key = key or func.__name__
            rate_config = RATE_LIMITS.get(rate_key, {
                "limit": limit or 100,
                "window": window or 60
            })
            
            # Initialize rate limiter
            rate_limiter = RateLimiter()
            identifier = rate_limiter.get_client_identifier(request)
            
            # Check rate limit
            is_allowed, info = rate_limiter.check_rate_limit(
                rate_key,
                rate_config["limit"],
                rate_config["window"],
                identifier
            )
            
            if not is_allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(info["reset_time"]),
                        "Retry-After": str(info["retry_after"]) if info["retry_after"] else "60"
                    }
                )
            
            # Continue with function
            return await func(request, *args, **kwargs)
            
        return wrapper
    return decorator


# Account lockout functionality
class AccountLockout:
    """Handle account lockout after failed attempts"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.lockout_duration = 1800  # 30 minutes
        self.max_attempts = 5
        
    def record_failed_attempt(self, identifier: str):
        """Record a failed login attempt"""
        key = f"failed_attempts:{identifier}"
        
        # Increment counter with expiration
        self.redis.incr(key)
        self.redis.expire(key, self.lockout_duration)
        
        # Check if account should be locked
        attempts = int(self.redis.get(key) or 0)
        if attempts >= self.max_attempts:
            self.lock_account(identifier)
            
    def lock_account(self, identifier: str):
        """Lock account for the lockout duration"""
        lock_key = f"account_locked:{identifier}"
        self.redis.setex(lock_key, self.lockout_duration, "locked")
        
        logger.warning(f"Account locked due to failed attempts: {identifier}")
        
    def is_account_locked(self, identifier: str) -> bool:
        """Check if account is currently locked"""
        lock_key = f"account_locked:{identifier}"
        return bool(self.redis.get(lock_key))
        
    def clear_failed_attempts(self, identifier: str):
        """Clear failed attempts after successful login"""
        attempts_key = f"failed_attempts:{identifier}"
        lock_key = f"account_locked:{identifier}"
        
        self.redis.delete(attempts_key, lock_key)
        
    def get_lockout_info(self, identifier: str) -> Dict:
        """Get lockout information for an identifier"""
        attempts_key = f"failed_attempts:{identifier}"
        lock_key = f"account_locked:{identifier}"
        
        attempts = int(self.redis.get(attempts_key) or 0)
        is_locked = bool(self.redis.get(lock_key))
        
        ttl = self.redis.ttl(lock_key) if is_locked else self.redis.ttl(attempts_key)
        
        return {
            "failed_attempts": attempts,
            "is_locked": is_locked,
            "remaining_lockout_time": ttl if ttl > 0 else 0,
            "max_attempts": self.max_attempts
        }