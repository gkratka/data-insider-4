from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal

class ExportRequest(BaseModel):
    """Base request schema for data export"""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    filename: Optional[str] = Field(None, description="Custom filename for export")
    filters: Optional[Dict[str, Any]] = Field(None, description="Data filters to apply before export")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Format-specific parameters")

class ChartExportRequest(BaseModel):
    """Request schema for chart export"""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    chart_type: str = Field(..., description="Type of chart to export")
    format: Literal["png", "svg", "html"] = Field("png", description="Export format")
    filename: Optional[str] = Field(None, description="Custom filename for export")
    filters: Optional[Dict[str, Any]] = Field(None, description="Data filters to apply")
    chart_parameters: Dict[str, Any] = Field(default_factory=dict, description="Chart-specific parameters")

class MultiFormatExportRequest(BaseModel):
    """Request schema for multi-format export"""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    formats: List[Literal["csv", "excel", "json"]] = Field(..., description="List of export formats")
    base_filename: Optional[str] = Field(None, description="Base filename for exports")
    filters: Optional[Dict[str, Any]] = Field(None, description="Data filters to apply")

class ExportResponse(BaseModel):
    """Response schema for export operations"""
    status: str
    export_type: str
    filename: str
    content: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: int
    rows: Optional[int] = None
    columns: Optional[int] = None
    metadata: Dict[str, Any]

class ExportCapabilitiesResponse(BaseModel):
    """Response schema for export capabilities"""
    status: str
    supported_formats: Dict[str, Dict[str, Any]]
    chart_export_formats: Dict[str, Dict[str, Any]]
    limitations: Dict[str, Any]

class CSVExportParameters(BaseModel):
    """Parameters specific to CSV export"""
    separator: str = Field(",", description="Column separator character")
    include_index: bool = Field(False, description="Include DataFrame index in export")
    custom_headers: Optional[List[str]] = Field(None, description="Custom column headers")
    date_format: Optional[str] = Field(None, description="Date formatting string")
    encoding: str = Field("utf-8", description="Character encoding")

class ExcelExportParameters(BaseModel):
    """Parameters specific to Excel export"""
    include_index: bool = Field(False, description="Include DataFrame index in export")
    multiple_sheets: bool = Field(False, description="Split data into multiple sheets")
    split_column: Optional[str] = Field(None, description="Column to split sheets by")
    sheet_names: Optional[List[str]] = Field(None, description="Custom sheet names")
    auto_format: bool = Field(True, description="Apply automatic formatting")

class JSONExportParameters(BaseModel):
    """Parameters specific to JSON export"""
    format_type: Literal["records", "index", "values", "split"] = Field("records", description="JSON structure format")
    include_metadata: bool = Field(True, description="Include export metadata")
    date_format: str = Field("iso", description="Date formatting")
    indent: int = Field(2, description="JSON indentation spaces")

class ChartExportParameters(BaseModel):
    """Parameters specific to chart export"""
    x_column: Optional[str] = Field(None, description="X-axis column")
    y_column: Optional[str] = Field(None, description="Y-axis column")
    column: Optional[str] = Field(None, description="Single column for histograms")
    bins: Optional[int] = Field(30, description="Number of bins for histograms")
    title: Optional[str] = Field(None, description="Chart title")
    width: int = Field(1200, description="Chart width in pixels")
    height: int = Field(800, description="Chart height in pixels")
    dpi: int = Field(300, description="Image resolution for static formats")

class ExportJobRequest(BaseModel):
    """Request schema for background export jobs"""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    export_type: Literal["csv", "excel", "json", "chart"] = Field(..., description="Type of export")
    filename: Optional[str] = Field(None, description="Custom filename")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Export parameters")
    notify_on_completion: bool = Field(True, description="Send notification when export completes")

class ExportJobResponse(BaseModel):
    """Response schema for export job submission"""
    job_id: str
    status: str
    export_type: str
    estimated_completion: str
    download_url: Optional[str] = None
    expires_at: Optional[str] = None

class ExportTemplate(BaseModel):
    """Schema for export templates"""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    export_type: str = Field(..., description="Export format")
    parameters: Dict[str, Any] = Field(..., description="Template parameters")
    use_cases: List[str] = Field(default_factory=list, description="Common use cases")

class ExportStatistics(BaseModel):
    """Schema for export usage statistics"""
    total_exports: int
    exports_by_format: Dict[str, int]
    average_file_size_mb: float
    most_exported_formats: List[str]
    peak_export_times: List[int]
    success_rate: float
    common_parameters: Dict[str, Any]