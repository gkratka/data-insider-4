from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.file import FileUploadResponse, FileMetadata
from app.services.file_service import FileService
from app.auth.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()
file_service = FileService()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Upload a file to the system
    
    Supports: CSV, Excel (.xlsx, .xls), JSON, Parquet files
    Maximum size: 500MB per file
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    user_id = current_user.id if current_user else None
    
    try:
        result = await file_service.save_uploaded_file(
            file=file,
            db=db,
            user_id=user_id,
            session_id=session_id
        )
        
        # Get the saved file record for response
        file_record = file_service.get_file_by_id(db, result['file_id'], user_id)
        
        return FileUploadResponse(
            id=file_record.id,
            filename=file_record.filename,
            original_filename=file_record.original_filename,
            file_size=file_record.file_size,
            file_type=file_record.file_type,
            mime_type=file_record.mime_type,
            upload_timestamp=file_record.upload_timestamp,
            row_count=file_record.row_count,
            column_count=file_record.column_count,
            columns_info=eval(file_record.columns_info) if file_record.columns_info else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=List[FileMetadata])
async def list_files(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    List uploaded files for the current user or session
    """
    if session_id:
        files = file_service.get_files_by_session(db, session_id)
    elif current_user:
        files = db.query(file_service.get_file_by_id.__self__.__class__).filter_by(user_id=current_user.id).all()
    else:
        files = []
    
    return [
        FileMetadata(
            id=f.id,
            filename=f.filename,
            original_filename=f.original_filename,
            file_size=f.file_size,
            file_type=f.file_type,
            upload_timestamp=f.upload_timestamp,
            row_count=f.row_count,
            column_count=f.column_count
        )
        for f in files
    ]


@router.get("/{file_id}", response_model=FileMetadata)
async def get_file_info(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get information about a specific file
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileMetadata(
        id=file_record.id,
        filename=file_record.filename,
        original_filename=file_record.original_filename,
        file_size=file_record.file_size,
        file_type=file_record.file_type,
        upload_timestamp=file_record.upload_timestamp,
        row_count=file_record.row_count,
        column_count=file_record.column_count
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Delete a file from the system
    """
    user_id = current_user.id if current_user else None
    
    success = file_service.delete_file(db, file_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="File not found or could not be deleted")
    
    return {"message": "File deleted successfully"}