from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class SessionCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    session_id: str
    db_session_id: Optional[int] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    last_activity: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None


class SessionUpdate(BaseModel):
    session_data: Dict[str, Any]


class SessionStats(BaseModel):
    session_id: str
    total_files: int
    total_size: int
    file_types: Dict[str, int]
    created_at: Optional[str] = None
    last_activity: Optional[str] = None


class SessionList(BaseModel):
    id: int
    session_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    is_active: str
    
    class Config:
        from_attributes = True