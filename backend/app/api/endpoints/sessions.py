from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate, SessionStats, SessionList
from app.services.session_service import SessionService
from app.auth.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()
session_service = SessionService()


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_create: SessionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Create a new data analysis session
    """
    user_id = current_user.id if current_user else None
    
    try:
        session_data = await session_service.create_session(
            db=db,
            user_id=user_id,
            name=session_create.name,
            description=session_create.description,
            session_data=session_create.session_data
        )
        
        return SessionResponse(**session_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get session information
    """
    session_data = await session_service.get_session(session_id, db)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check access permissions
    if current_user and session_data.get('user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return SessionResponse(**session_data)


@router.put("/{session_id}/data", response_model=dict)
async def update_session_data(
    session_id: str,
    session_update: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Update session data
    """
    # Verify session exists and user has access
    session_data = await session_service.get_session(session_id, db)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user and session_data.get('user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await session_service.update_session_data(
        session_id, 
        session_update.session_data,
        db
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update session data")
    
    return {"message": "Session data updated successfully"}


@router.get("/{session_id}/stats", response_model=SessionStats)
async def get_session_stats(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get session statistics
    """
    # Verify session exists
    session_data = await session_service.get_session(session_id, db)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user and session_data.get('user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    stats = await session_service.get_session_stats(session_id, db)
    return SessionStats(**stats)


@router.get("/", response_model=List[SessionList])
async def list_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    List all sessions for the current user
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    sessions = session_service.get_user_sessions(db, current_user.id)
    return [SessionList.from_orm(session) for session in sessions]


@router.delete("/{session_id}")
async def close_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Close a session
    """
    # Verify session exists and user has access
    session_data = await session_service.get_session(session_id, db)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user and session_data.get('user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await session_service.close_session(session_id, db)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to close session")
    
    return {"message": "Session closed successfully"}