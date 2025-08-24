import os
import magic
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class FileValidator:
    """File validation utility for uploaded files"""
    
    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
    SUPPORTED_MIME_TYPES = {
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'application/json',
        'application/octet-stream'  # for parquet files
    }
    
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    
    @classmethod
    def validate_file(cls, file_path: str, original_filename: str) -> Dict[str, any]:
        """
        Validate uploaded file and return validation results
        
        Args:
            file_path: Path to uploaded file
            original_filename: Original filename from upload
            
        Returns:
            Dict with validation results and file info
        """
        result = {
            'is_valid': True,
            'errors': [],
            'file_info': {}
        }
        
        try:
            # Check file exists
            if not os.path.exists(file_path):
                result['is_valid'] = False
                result['errors'].append('File does not exist')
                return result
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > cls.MAX_FILE_SIZE:
                result['is_valid'] = False
                result['errors'].append(f'File size ({file_size} bytes) exceeds maximum allowed size ({cls.MAX_FILE_SIZE} bytes)')
            
            # Check file extension
            file_ext = Path(original_filename).suffix.lower()
            if file_ext not in cls.SUPPORTED_EXTENSIONS:
                result['is_valid'] = False
                result['errors'].append(f'Unsupported file extension: {file_ext}. Supported: {", ".join(cls.SUPPORTED_EXTENSIONS)}')
            
            # Detect MIME type
            try:
                mime_type = magic.from_file(file_path, mime=True)
            except:
                mime_type = 'application/octet-stream'
            
            # Map file extension to file type
            file_type_mapping = {
                '.csv': 'csv',
                '.xlsx': 'excel',
                '.xls': 'excel',
                '.json': 'json',
                '.parquet': 'parquet'
            }
            
            file_type = file_type_mapping.get(file_ext, 'unknown')
            
            # Store file info
            result['file_info'] = {
                'file_size': file_size,
                'mime_type': mime_type,
                'file_type': file_type,
                'file_extension': file_ext
            }
            
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f'Validation error: {str(e)}')
        
        return result
    
    @classmethod
    def get_safe_filename(cls, filename: str) -> str:
        """
        Generate a safe filename for storage
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename string
        """
        import uuid
        import datetime
        
        # Get file extension
        file_ext = Path(filename).suffix.lower()
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{timestamp}_{unique_id}{file_ext}"