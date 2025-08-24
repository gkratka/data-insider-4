import os
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import pandas as pd
import json

from app.models.file import UploadedFile
from app.utils.file_validator import FileValidator


class FileService:
    """Service for handling file uploads and management"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_file(
        self,
        file: UploadFile,
        db: Session,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Save uploaded file to storage and database
        
        Args:
            file: FastAPI UploadFile object
            db: Database session
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            Dict with saved file information
        """
        try:
            # Generate safe filename
            safe_filename = FileValidator.get_safe_filename(file.filename)
            file_path = self.upload_dir / safe_filename
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Validate file
            validation_result = FileValidator.validate_file(str(file_path), file.filename)
            
            if not validation_result['is_valid']:
                # Remove invalid file
                os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File validation failed: {'; '.join(validation_result['errors'])}"
                )
            
            file_info = validation_result['file_info']
            
            # Extract data metadata
            metadata = await self._extract_file_metadata(str(file_path), file_info['file_type'])
            
            # Create database record
            db_file = UploadedFile(
                filename=safe_filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_info['file_size'],
                file_type=file_info['file_type'],
                mime_type=file_info['mime_type'],
                user_id=user_id,
                session_id=session_id,
                row_count=metadata.get('row_count'),
                column_count=metadata.get('column_count'),
                columns_info=json.dumps(metadata.get('columns_info', {}))
            )
            
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            
            return {
                'file_id': db_file.id,
                'filename': safe_filename,
                'original_filename': file.filename,
                'file_size': file_info['file_size'],
                'file_type': file_info['file_type'],
                'metadata': metadata
            }
            
        except Exception as e:
            # Clean up file if database operation fails
            if file_path.exists():
                os.remove(file_path)
            
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    async def _extract_file_metadata(self, file_path: str, file_type: str) -> Dict[str, any]:
        """
        Extract metadata from uploaded file
        
        Args:
            file_path: Path to file
            file_type: Type of file (csv, excel, json, parquet)
            
        Returns:
            Dict with file metadata
        """
        metadata = {}
        
        try:
            if file_type == 'csv':
                df = pd.read_csv(file_path, nrows=0)  # Just get column info
                metadata.update(self._get_dataframe_metadata(df))
                
                # Get row count efficiently
                with open(file_path, 'r', encoding='utf-8') as f:
                    row_count = sum(1 for _ in f) - 1  # Subtract header
                metadata['row_count'] = max(0, row_count)
                
            elif file_type == 'excel':
                df = pd.read_excel(file_path, nrows=0)  # Just get column info
                metadata.update(self._get_dataframe_metadata(df))
                
                # Get row count from Excel
                full_df = pd.read_excel(file_path, nrows=None)
                metadata['row_count'] = len(full_df)
                
            elif file_type == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and len(data) > 0:
                    # JSON array of objects
                    metadata['row_count'] = len(data)
                    if isinstance(data[0], dict):
                        metadata['column_count'] = len(data[0].keys())
                        metadata['columns_info'] = {k: 'mixed' for k in data[0].keys()}
                elif isinstance(data, dict):
                    # Single JSON object
                    metadata['row_count'] = 1
                    metadata['column_count'] = len(data.keys())
                    metadata['columns_info'] = {k: type(v).__name__ for k, v in data.items()}
                
            elif file_type == 'parquet':
                df = pd.read_parquet(file_path)
                metadata.update(self._get_dataframe_metadata(df))
                metadata['row_count'] = len(df)
                
        except Exception as e:
            # If metadata extraction fails, return basic info
            metadata = {
                'row_count': None,
                'column_count': None,
                'columns_info': {},
                'extraction_error': str(e)
            }
        
        return metadata
    
    def _get_dataframe_metadata(self, df: pd.DataFrame) -> Dict[str, any]:
        """Extract metadata from pandas DataFrame"""
        return {
            'column_count': len(df.columns),
            'columns_info': {col: str(df[col].dtype) for col in df.columns}
        }
    
    def get_file_by_id(self, db: Session, file_id: int, user_id: Optional[int] = None) -> Optional[UploadedFile]:
        """Get file by ID with optional user filtering"""
        query = db.query(UploadedFile).filter(UploadedFile.id == file_id)
        
        if user_id:
            query = query.filter(UploadedFile.user_id == user_id)
        
        return query.first()
    
    def get_files_by_session(self, db: Session, session_id: str) -> List[UploadedFile]:
        """Get all files for a session"""
        return db.query(UploadedFile).filter(UploadedFile.session_id == session_id).all()
    
    def delete_file(self, db: Session, file_id: int, user_id: Optional[int] = None) -> bool:
        """Delete file from storage and database"""
        file_record = self.get_file_by_id(db, file_id, user_id)
        
        if not file_record:
            return False
        
        try:
            # Remove file from disk
            if os.path.exists(file_record.file_path):
                os.remove(file_record.file_path)
            
            # Remove database record
            db.delete(file_record)
            db.commit()
            
            return True
        except Exception:
            db.rollback()
            return False