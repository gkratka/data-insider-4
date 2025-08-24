from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional, Any
import base64
import io
from app.services.export_service import DataExportService, ExportFormat
from app.services.data_processing_service import DataProcessingService
from app.services.session_service import SessionService
from app.schemas.export import (
    ExportRequest,
    ChartExportRequest,
    MultiFormatExportRequest,
    ExportResponse
)

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/csv")
async def export_to_csv(
    request: ExportRequest,
    export_service: DataExportService = Depends(DataExportService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Export data to CSV format"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Apply filters if provided
        if request.filters:
            df = await data_service.filter_data(df, request.filters)
        
        # Export to CSV
        result = await export_service.export_data_to_csv(
            data=df,
            filename=request.filename,
            separator=request.parameters.get("separator", ","),
            include_index=request.parameters.get("include_index", False),
            custom_headers=request.parameters.get("custom_headers"),
            date_format=request.parameters.get("date_format")
        )
        
        return {
            "status": "success",
            "export_type": "csv",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")


@router.post("/excel")
async def export_to_excel(
    request: ExportRequest,
    export_service: DataExportService = Depends(DataExportService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Export data to Excel format"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Apply filters if provided
        if request.filters:
            df = await data_service.filter_data(df, request.filters)
        
        # Handle multiple sheets if specified
        data_for_export = df
        if request.parameters.get("multiple_sheets"):
            # Split data by a column for multiple sheets
            split_column = request.parameters.get("split_column")
            if split_column and split_column in df.columns:
                data_for_export = {}
                for value in df[split_column].unique():
                    sheet_data = df[df[split_column] == value]
                    sheet_name = str(value)[:31]  # Excel sheet name limit
                    data_for_export[sheet_name] = sheet_data
            else:
                data_for_export = {"Sheet1": df}
        
        # Export to Excel
        result = await export_service.export_data_to_excel(
            data=data_for_export,
            filename=request.filename,
            include_index=request.parameters.get("include_index", False),
            sheet_names=request.parameters.get("sheet_names")
        )
        
        return {
            "status": "success",
            "export_type": "excel",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}")


@router.post("/json")
async def export_to_json(
    request: ExportRequest,
    export_service: DataExportService = Depends(DataExportService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Export data to JSON format"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Apply filters if provided
        if request.filters:
            df = await data_service.filter_data(df, request.filters)
        
        # Export to JSON
        result = await export_service.export_data_to_json(
            data=df,
            filename=request.filename,
            format_type=request.parameters.get("format_type", "records"),
            include_metadata=request.parameters.get("include_metadata", True),
            date_format=request.parameters.get("date_format", "iso")
        )
        
        return {
            "status": "success",
            "export_type": "json",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON export failed: {str(e)}")


@router.post("/chart")
async def export_chart(
    request: ChartExportRequest,
    export_service: DataExportService = Depends(DataExportService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Export chart visualization to image format"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Apply filters if provided
        if request.filters:
            df = await data_service.filter_data(df, request.filters)
        
        # Export chart
        result = await export_service.export_chart_to_image(
            data=df,
            chart_type=request.chart_type,
            format=request.format,
            filename=request.filename,
            **request.chart_parameters
        )
        
        return {
            "status": "success",
            "export_type": "chart",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart export failed: {str(e)}")


@router.post("/multiple-formats")
async def export_multiple_formats(
    request: MultiFormatExportRequest,
    export_service: DataExportService = Depends(DataExportService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Export data to multiple formats simultaneously"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Apply filters if provided
        if request.filters:
            df = await data_service.filter_data(df, request.filters)
        
        # Export to multiple formats
        result = await export_service.export_multiple_formats(
            data=df,
            formats=request.formats,
            base_filename=request.base_filename
        )
        
        return {
            "status": "success",
            "export_type": "multiple_formats",
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple format export failed: {str(e)}")


@router.get("/download/{export_id}")
async def download_export(
    export_id: str,
    format: str = "csv",
    # In a real implementation, you'd retrieve the export from storage
    # For now, this is a placeholder for the download endpoint
) -> StreamingResponse:
    """Download exported file by ID"""
    try:
        # This would typically retrieve the export from Redis/database
        # For now, return a placeholder response
        
        content_types = {
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json",
            "png": "image/png",
            "svg": "image/svg+xml"
        }
        
        # Placeholder content
        content = "placeholder export content"
        filename = f"export_{export_id}.{format}"
        
        return StreamingResponse(
            io.StringIO(content),
            media_type=content_types.get(format, "application/octet-stream"),
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/capabilities")
async def get_export_capabilities(
    export_service: DataExportService = Depends(DataExportService)
) -> Dict[str, Any]:
    """Get available export capabilities and formats"""
    try:
        capabilities = await export_service.get_export_capabilities()
        return {
            "status": "success",
            **capabilities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")


@router.get("/templates")
async def get_export_templates() -> Dict[str, Any]:
    """Get predefined export templates and examples"""
    return {
        "csv_templates": [
            {
                "name": "Standard CSV",
                "description": "Basic CSV with comma separator",
                "parameters": {
                    "separator": ",",
                    "include_index": False,
                    "date_format": "%Y-%m-%d"
                }
            },
            {
                "name": "European CSV",
                "description": "CSV with semicolon separator for European locale",
                "parameters": {
                    "separator": ";",
                    "include_index": False,
                    "date_format": "%d/%m/%Y"
                }
            }
        ],
        "excel_templates": [
            {
                "name": "Single Sheet",
                "description": "All data in one sheet",
                "parameters": {
                    "include_index": False,
                    "multiple_sheets": False
                }
            },
            {
                "name": "Multi-Sheet by Category",
                "description": "Split data into sheets by categorical column",
                "parameters": {
                    "include_index": False,
                    "multiple_sheets": True,
                    "split_column": "category"
                }
            }
        ],
        "json_templates": [
            {
                "name": "Records Format",
                "description": "Array of objects (records)",
                "parameters": {
                    "format_type": "records",
                    "include_metadata": True
                }
            },
            {
                "name": "Split Format",
                "description": "Separate columns, index, and data",
                "parameters": {
                    "format_type": "split",
                    "include_metadata": True
                }
            }
        ],
        "chart_templates": [
            {
                "name": "Line Chart",
                "chart_type": "line",
                "parameters": {
                    "x_column": "date",
                    "y_column": "value"
                }
            },
            {
                "name": "Bar Chart",
                "chart_type": "bar", 
                "parameters": {
                    "x_column": "category",
                    "y_column": "count"
                }
            },
            {
                "name": "Scatter Plot",
                "chart_type": "scatter",
                "parameters": {
                    "x_column": "x_var",
                    "y_column": "y_var"
                }
            },
            {
                "name": "Histogram",
                "chart_type": "histogram",
                "parameters": {
                    "column": "numeric_column",
                    "bins": 30
                }
            }
        ]
    }