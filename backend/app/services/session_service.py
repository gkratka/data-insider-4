from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import redis.asyncio as redis

from app.models.session import DataSession, RedisSessionManager
from app.models.user import User
from app.models.file import UploadedFile


class SessionService:
    """Service for managing user data sessions"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.redis_session_manager = RedisSessionManager(self.redis_client)
    
    async def create_session(
        self,
        db: Session,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        session_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new data session
        
        Args:
            db: Database session
            user_id: Optional user ID
            name: Optional session name
            description: Optional session description
            session_data: Initial session data
            
        Returns:
            Dict with session information
        """
        # Create database session record
        db_session = DataSession(
            user_id=user_id,
            name=name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description=description,
            session_data=session_data or {}
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        # Create Redis session for fast access
        redis_session_id = await self.redis_session_manager.create_session(
            user_id=user_id,
            session_data={
                'db_session_id': db_session.id,
                'name': db_session.name,
                'description': db_session.description,
                **session_data or {}
            }
        )
        
        return {
            'session_id': redis_session_id,
            'db_session_id': db_session.id,
            'user_id': user_id,
            'name': db_session.name,
            'description': db_session.description,
            'created_at': db_session.created_at,
            'session_data': session_data or {}
        }
    
    async def get_session(self, session_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        # First try Redis for fast access
        redis_session = await self.redis_session_manager.get_session(session_id)
        
        if not redis_session:
            return None
        
        # Get additional data from database if needed
        db_session_id = redis_session.get('session_data', {}).get('db_session_id')
        if db_session_id:
            db_session = db.query(DataSession).filter(DataSession.id == db_session_id).first()
            if db_session:
                redis_session.update({
                    'name': db_session.name,
                    'description': db_session.description,
                    'updated_at': db_session.updated_at,
                    'expires_at': db_session.expires_at
                })
        
        return redis_session
    
    async def update_session_data(
        self,
        session_id: str,
        data: Dict[str, Any],
        db: Session
    ) -> bool:
        """Update session data"""
        # Update Redis
        success = await self.redis_session_manager.update_session_data(session_id, data)
        
        if success:
            # Update database record if it exists
            redis_session = await self.redis_session_manager.get_session(session_id)
            if redis_session:
                db_session_id = redis_session.get('session_data', {}).get('db_session_id')
                if db_session_id:
                    db_session = db.query(DataSession).filter(DataSession.id == db_session_id).first()
                    if db_session:
                        db_session.session_data = data
                        db_session.last_activity = datetime.utcnow()
                        db.commit()
        
        return success
    
    def get_session_files(self, db: Session, session_id: str) -> List[UploadedFile]:
        """Get all files associated with a session"""
        return db.query(UploadedFile).filter(UploadedFile.session_id == session_id).all()
    
    def get_user_sessions(self, db: Session, user_id: int) -> List[DataSession]:
        """Get all sessions for a user from database"""
        return db.query(DataSession).filter(
            DataSession.user_id == user_id,
            DataSession.is_active == 'active'
        ).order_by(DataSession.updated_at.desc()).all()
    
    async def close_session(self, session_id: str, db: Session) -> bool:
        """Close a session"""
        # Update database record
        redis_session = await self.redis_session_manager.get_session(session_id)
        if redis_session:
            db_session_id = redis_session.get('session_data', {}).get('db_session_id')
            if db_session_id:
                db_session = db.query(DataSession).filter(DataSession.id == db_session_id).first()
                if db_session:
                    db_session.is_active = 'closed'
                    db.commit()
        
        # Remove from Redis
        return await self.redis_session_manager.delete_session(session_id)
    
    async def cleanup_expired_sessions(self, db: Session):
        """Clean up expired sessions"""
        # Clean up Redis sessions
        await self.redis_session_manager.cleanup_expired_sessions()
        
        # Mark expired database sessions
        expired_sessions = db.query(DataSession).filter(
            DataSession.expires_at < datetime.utcnow(),
            DataSession.is_active == 'active'
        ).all()
        
        for session in expired_sessions:
            session.is_active = 'expired'
        
        db.commit()
    
    async def get_session_stats(self, session_id: str, db: Session) -> Dict[str, Any]:
        """Get session statistics"""
        session_data = await self.get_session(session_id, db)
        if not session_data:
            return {}
        
        # Get file count and size
        files = self.get_session_files(db, session_id)
        total_files = len(files)
        total_size = sum(f.file_size for f in files)
        
        # Get file types
        file_types = {}
        for f in files:
            file_types[f.file_type] = file_types.get(f.file_type, 0) + 1
        
        return {
            'session_id': session_id,
            'total_files': total_files,
            'total_size': total_size,
            'file_types': file_types,
            'created_at': session_data.get('created_at'),
            'last_activity': session_data.get('last_activity')
        }