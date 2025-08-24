from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timedelta
import uuid


class DataSession(Base):
    """User session for tracking data analysis workflows"""
    __tablename__ = "data_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional for anonymous sessions
    
    # Session metadata
    name = Column(String(255), nullable=True)  # User-defined session name
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=24))
    last_activity = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Session data
    session_data = Column(JSON, default={})  # Store conversation context, user preferences, etc.
    
    # Status
    is_active = Column(String(20), default='active')  # active, expired, closed
    
    # Relationships
    user = relationship("User", back_populates="data_sessions")


class RedisSessionManager:
    """Redis-based session management for performance"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.session_ttl = 86400  # 24 hours
    
    async def create_session(self, user_id: int = None, session_data: dict = None) -> str:
        """Create a new session in Redis"""
        session_id = str(uuid.uuid4())
        session_key = f"{self.session_prefix}{session_id}"
        
        session_info = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'session_data': session_data or {}
        }
        
        # Store in Redis with TTL
        await self.redis.hset(session_key, mapping={k: str(v) for k, v in session_info.items()})
        await self.redis.expire(session_key, self.session_ttl)
        
        # Track user sessions if user_id provided
        if user_id:
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            await self.redis.sadd(user_sessions_key, session_id)
            await self.redis.expire(user_sessions_key, self.session_ttl)
        
        return session_id
    
    async def get_session(self, session_id: str) -> dict:
        """Get session data from Redis"""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis.hgetall(session_key)
        
        if not session_data:
            return None
        
        # Update last activity
        await self.redis.hset(session_key, 'last_activity', datetime.utcnow().isoformat())
        await self.redis.expire(session_key, self.session_ttl)
        
        return {
            'session_id': session_data.get('session_id'),
            'user_id': int(session_data.get('user_id')) if session_data.get('user_id') != 'None' else None,
            'created_at': session_data.get('created_at'),
            'last_activity': session_data.get('last_activity'),
            'session_data': eval(session_data.get('session_data', '{}'))
        }
    
    async def update_session_data(self, session_id: str, data: dict) -> bool:
        """Update session data in Redis"""
        session_key = f"{self.session_prefix}{session_id}"
        
        # Check if session exists
        if not await self.redis.exists(session_key):
            return False
        
        # Update session data
        await self.redis.hset(session_key, mapping={
            'session_data': str(data),
            'last_activity': datetime.utcnow().isoformat()
        })
        await self.redis.expire(session_key, self.session_ttl)
        
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        session_key = f"{self.session_prefix}{session_id}"
        
        # Get session info first to remove from user sessions
        session_info = await self.redis.hgetall(session_key)
        
        if session_info and session_info.get('user_id') != 'None':
            user_id = session_info.get('user_id')
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            await self.redis.srem(user_sessions_key, session_id)
        
        # Delete session
        return bool(await self.redis.delete(session_key))
    
    async def get_user_sessions(self, user_id: int) -> list:
        """Get all sessions for a user"""
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_ids = await self.redis.smembers(user_sessions_key)
        
        sessions = []
        for session_id in session_ids:
            session_data = await self.get_session(session_id.decode())
            if session_data:
                sessions.append(session_data)
        
        return sessions
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions (run as background task)"""
        pattern = f"{self.session_prefix}*"
        async for key in self.redis.scan_iter(match=pattern):
            ttl = await self.redis.ttl(key)
            if ttl == -1:  # No expiry set
                await self.redis.expire(key, self.session_ttl)