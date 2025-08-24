import pytest
import tempfile
import os
from fastapi import UploadFile
from io import BytesIO
from app.services.file_service import FileService
from app.schemas.file import FileUpload, FileMetadata

@pytest.fixture
def file_service():
    return FileService()

@pytest.fixture
def csv_file():
    csv_content = "id,name,age\n1,John,30\n2,Jane,25\n"
    return UploadFile(
        filename="test.csv",
        file=BytesIO(csv_content.encode()),
        headers={"content-type": "text/csv"}
    )

@pytest.fixture
def excel_file():
    # Mock Excel file content
    excel_content = b'\x50\x4b\x03\x04' # ZIP signature for xlsx files
    return UploadFile(
        filename="test.xlsx",
        file=BytesIO(excel_content),
        headers={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    )

class TestFileService:
    
    def test_validate_file_csv(self, file_service, csv_file):
        """Test CSV file validation"""
        is_valid = file_service.validate_file(csv_file)
        assert is_valid is True
        
    def test_validate_file_excel(self, file_service, excel_file):
        """Test Excel file validation"""
        is_valid = file_service.validate_file(excel_file)
        assert is_valid is True
        
    def test_validate_file_invalid_type(self, file_service):
        """Test invalid file type rejection"""
        invalid_file = UploadFile(
            filename="test.txt",
            file=BytesIO(b"some text"),
            headers={"content-type": "text/plain"}
        )
        is_valid = file_service.validate_file(invalid_file)
        assert is_valid is False
        
    def test_validate_file_size_limit(self, file_service):
        """Test file size validation"""
        large_content = b"x" * (501 * 1024 * 1024)  # 501MB
        large_file = UploadFile(
            filename="large.csv",
            file=BytesIO(large_content),
            headers={"content-type": "text/csv"}
        )
        
        is_valid = file_service.validate_file(large_file)
        assert is_valid is False
        
    def test_extract_metadata_csv(self, file_service, csv_file):
        """Test metadata extraction for CSV files"""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
            tmp.write("id,name,age\n1,John,30\n2,Jane,25\n")
            tmp_path = tmp.name
            
        try:
            metadata = file_service.extract_metadata(tmp_path, "csv")
            assert metadata.row_count == 2  # Excluding header
            assert metadata.column_count == 3
            assert "id" in metadata.columns
            assert "name" in metadata.columns
            assert "age" in metadata.columns
        finally:
            os.unlink(tmp_path)
            
    def test_get_file_preview_csv(self, file_service):
        """Test CSV file preview generation"""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
            tmp.write("id,name,age\n1,John,30\n2,Jane,25\n3,Bob,35\n")
            tmp_path = tmp.name
            
        try:
            preview = file_service.get_file_preview(tmp_path, "csv", limit=2)
            assert len(preview.headers) == 3
            assert len(preview.rows) == 2
            assert preview.headers == ["id", "name", "age"]
            assert preview.rows[0] == ["1", "John", "30"]
            assert preview.total_rows == 3
        finally:
            os.unlink(tmp_path)
            
    def test_delete_file(self, file_service):
        """Test file deletion"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name
            
        # File should exist
        assert os.path.exists(tmp_path)
        
        # Delete file
        file_service.delete_file(tmp_path)
        
        # File should be deleted
        assert not os.path.exists(tmp_path)
        
    def test_get_supported_formats(self, file_service):
        """Test getting supported file formats"""
        formats = file_service.get_supported_formats()
        expected_formats = ["csv", "xlsx", "xls", "json", "parquet"]
        
        for fmt in expected_formats:
            assert fmt in formats
            
    def test_format_file_size(self, file_service):
        """Test file size formatting"""
        assert file_service.format_file_size(1024) == "1.0 KB"
        assert file_service.format_file_size(1024 * 1024) == "1.0 MB"
        assert file_service.format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert file_service.format_file_size(500) == "500 B"