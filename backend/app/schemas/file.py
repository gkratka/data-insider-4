from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class FileUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    upload_timestamp: datetime
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    columns_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class FileMetadata(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class FileValidationError(BaseModel):
    detail: str
    error_type: str
    field: Optional[str] = None