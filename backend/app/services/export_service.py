import io
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import pandas as pd
import numpy as np
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.io as pio
from app.services.data_processing_service import DataProcessingService

logger = logging.getLogger(__name__)

class ExportFormat:
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PARQUET = "parquet"
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    HTML = "html"

class DataExportService:
    """Service for exporting data and visualizations in various formats"""
    
    def __init__(self):
        self.data_service = DataProcessingService()
        self.max_export_rows = 1000000  # 1M row limit for exports
        
    async def export_data_to_csv(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        separator: str = ",",
        include_index: bool = False,
        custom_headers: Optional[List[str]] = None,
        date_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export DataFrame to CSV format"""
        try:
            if len(data) > self.max_export_rows:
                raise ValueError(f"Dataset too large for export. Max {self.max_export_rows:,} rows allowed.")
            
            # Apply custom headers if provided
            if custom_headers and len(custom_headers) == len(data.columns):
                data = data.copy()
                data.columns = custom_headers
            
            # Generate CSV content
            csv_buffer = io.StringIO()
            data.to_csv(
                csv_buffer,
                sep=separator,
                index=include_index,
                date_format=date_format,
                float_format='%.6f'  # Control decimal precision
            )
            
            csv_content = csv_buffer.getvalue()
            csv_buffer.close()
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_export_{timestamp}.csv"
            
            return {
                'format': ExportFormat.CSV,
                'filename': filename,
                'content': csv_content,
                'size_bytes': len(csv_content.encode('utf-8')),
                'rows': len(data),
                'columns': len(data.columns),
                'separator': separator,
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'original_columns': data.columns.tolist(),
                    'data_types': data.dtypes.astype(str).to_dict()
                }
            }
            
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}")
            raise Exception(f"CSV export failed: {str(e)}")
    
    async def export_data_to_excel(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        filename: Optional[str] = None,
        include_index: bool = False,
        sheet_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Export DataFrame(s) to Excel format with multiple sheets"""
        try:
            # Handle single DataFrame
            if isinstance(data, pd.DataFrame):
                if len(data) > self.max_export_rows:
                    raise ValueError(f"Dataset too large for export. Max {self.max_export_rows:,} rows allowed.")
                data = {'Sheet1': data}
            
            # Validate total rows across all sheets
            total_rows = sum(len(df) for df in data.values())
            if total_rows > self.max_export_rows:
                raise ValueError(f"Total dataset too large for export. Max {self.max_export_rows:,} rows allowed.")
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_export_{timestamp}.xlsx"
            
            # Create Excel file in memory
            excel_buffer = io.BytesIO()
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                for i, (sheet_name, df) in enumerate(data.items()):
                    # Use provided sheet names or default naming
                    if sheet_names and i < len(sheet_names):
                        sheet_name = sheet_names[i]
                    
                    # Write DataFrame to sheet
                    df.to_excel(
                        writer,
                        sheet_name=sheet_name[:31],  # Excel sheet name limit
                        index=include_index,
                        float_format='%.6f'
                    )
                    
                    # Get worksheet for formatting
                    worksheet = writer.sheets[sheet_name[:31]]
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            excel_content = excel_buffer.getvalue()
            excel_buffer.close()
            
            return {
                'format': ExportFormat.EXCEL,
                'filename': filename,
                'content': base64.b64encode(excel_content).decode('utf-8'),
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'size_bytes': len(excel_content),
                'sheets': list(data.keys()),
                'total_rows': total_rows,
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'sheet_info': {
                        name: {
                            'rows': len(df),
                            'columns': len(df.columns),
                            'column_names': df.columns.tolist()
                        }
                        for name, df in data.items()
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise Exception(f"Excel export failed: {str(e)}")
    
    async def export_data_to_json(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        format_type: str = "records",
        include_metadata: bool = True,
        date_format: str = "iso"
    ) -> Dict[str, Any]:
        """Export DataFrame to JSON format"""
        try:
            if len(data) > self.max_export_rows:
                raise ValueError(f"Dataset too large for export. Max {self.max_export_rows:,} rows allowed.")
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_export_{timestamp}.json"
            
            # Convert DataFrame to JSON
            if format_type == "records":
                json_data = data.to_dict('records')
            elif format_type == "index":
                json_data = data.to_dict('index')
            elif format_type == "values":
                json_data = data.values.tolist()
            elif format_type == "split":
                json_data = {
                    'columns': data.columns.tolist(),
                    'index': data.index.tolist(),
                    'data': data.values.tolist()
                }
            else:
                json_data = data.to_dict(format_type)
            
            # Add metadata if requested
            if include_metadata:
                export_data = {
                    'metadata': {
                        'export_timestamp': datetime.utcnow().isoformat(),
                        'format_type': format_type,
                        'rows': len(data),
                        'columns': len(data.columns),
                        'column_names': data.columns.tolist(),
                        'data_types': data.dtypes.astype(str).to_dict()
                    },
                    'data': json_data
                }
            else:
                export_data = json_data
            
            # Serialize to JSON string
            json_content = json.dumps(
                export_data,
                default=self._json_serializer,
                indent=2,
                ensure_ascii=False
            )
            
            return {
                'format': ExportFormat.JSON,
                'filename': filename,
                'content': json_content,
                'content_type': 'application/json',
                'size_bytes': len(json_content.encode('utf-8')),
                'rows': len(data),
                'columns': len(data.columns),
                'format_type': format_type,
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'include_metadata': include_metadata
                }
            }
            
        except Exception as e:
            logger.error(f"JSON export failed: {str(e)}")
            raise Exception(f"JSON export failed: {str(e)}")
    
    async def export_chart_to_image(
        self,
        data: pd.DataFrame,
        chart_type: str,
        format: str = "png",
        filename: Optional[str] = None,
        **chart_params
    ) -> Dict[str, Any]:
        """Export chart visualization to image format"""
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chart_{chart_type}_{timestamp}.{format}"
            
            image_content = None
            
            if chart_type in ["line", "bar", "scatter", "histogram", "heatmap"]:
                # Use matplotlib/seaborn for static charts
                plt.figure(figsize=(12, 8))
                
                if chart_type == "line":
                    x_col = chart_params.get("x_column", data.columns[0])
                    y_col = chart_params.get("y_column", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                    plt.plot(data[x_col], data[y_col])
                    plt.xlabel(x_col)
                    plt.ylabel(y_col)
                    plt.title(f"{y_col} vs {x_col}")
                    
                elif chart_type == "bar":
                    x_col = chart_params.get("x_column", data.columns[0])
                    y_col = chart_params.get("y_column", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                    plt.bar(data[x_col], data[y_col])
                    plt.xlabel(x_col)
                    plt.ylabel(y_col)
                    plt.title(f"{y_col} by {x_col}")
                    plt.xticks(rotation=45)
                    
                elif chart_type == "scatter":
                    x_col = chart_params.get("x_column", data.columns[0])
                    y_col = chart_params.get("y_column", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                    plt.scatter(data[x_col], data[y_col], alpha=0.6)
                    plt.xlabel(x_col)
                    plt.ylabel(y_col)
                    plt.title(f"{y_col} vs {x_col}")
                    
                elif chart_type == "histogram":
                    column = chart_params.get("column", data.select_dtypes(include=[np.number]).columns[0])
                    bins = chart_params.get("bins", 30)
                    plt.hist(data[column].dropna(), bins=bins, alpha=0.7, edgecolor='black')
                    plt.xlabel(column)
                    plt.ylabel("Frequency")
                    plt.title(f"Distribution of {column}")
                    
                elif chart_type == "heatmap":
                    # Correlation heatmap for numeric columns
                    numeric_data = data.select_dtypes(include=[np.number])
                    if len(numeric_data.columns) > 1:
                        corr_matrix = numeric_data.corr()
                        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
                        plt.title("Correlation Heatmap")
                    else:
                        raise ValueError("Need at least 2 numeric columns for correlation heatmap")
                
                plt.tight_layout()
                
                # Save to buffer
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format=format, dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                image_content = img_buffer.getvalue()
                img_buffer.close()
                plt.close()
                
            elif chart_type in ["interactive_line", "interactive_bar", "interactive_scatter"]:
                # Use Plotly for interactive charts
                if chart_type == "interactive_line":
                    x_col = chart_params.get("x_column", data.columns[0])
                    y_col = chart_params.get("y_column", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                    fig = go.Figure(data=go.Scatter(x=data[x_col], y=data[y_col], mode='lines'))
                    fig.update_layout(title=f"{y_col} vs {x_col}", xaxis_title=x_col, yaxis_title=y_col)
                    
                elif chart_type == "interactive_bar":
                    x_col = chart_params.get("x_column", data.columns[0])
                    y_col = chart_params.get("y_column", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                    fig = go.Figure(data=go.Bar(x=data[x_col], y=data[y_col]))
                    fig.update_layout(title=f"{y_col} by {x_col}", xaxis_title=x_col, yaxis_title=y_col)
                    
                elif chart_type == "interactive_scatter":
                    x_col = chart_params.get("x_column", data.columns[0])
                    y_col = chart_params.get("y_column", data.columns[1] if len(data.columns) > 1 else data.columns[0])
                    fig = go.Figure(data=go.Scatter(x=data[x_col], y=data[y_col], mode='markers'))
                    fig.update_layout(title=f"{y_col} vs {x_col}", xaxis_title=x_col, yaxis_title=y_col)
                
                # Export Plotly chart
                if format == "png":
                    image_content = pio.to_image(fig, format="png", width=1200, height=800, scale=2)
                elif format == "svg":
                    image_content = pio.to_image(fig, format="svg", width=1200, height=800).decode('utf-8').encode('utf-8')
                elif format == "html":
                    image_content = pio.to_html(fig, include_plotlyjs=True).encode('utf-8')
            
            if not image_content:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            # Determine content type
            content_type_map = {
                'png': 'image/png',
                'svg': 'image/svg+xml',
                'html': 'text/html'
            }
            
            return {
                'format': format.upper(),
                'filename': filename,
                'content': base64.b64encode(image_content).decode('utf-8') if format != 'html' else image_content.decode('utf-8'),
                'content_type': content_type_map.get(format, 'application/octet-stream'),
                'size_bytes': len(image_content),
                'chart_type': chart_type,
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'chart_parameters': chart_params,
                    'data_shape': data.shape
                }
            }
            
        except Exception as e:
            logger.error(f"Chart export failed: {str(e)}")
            raise Exception(f"Chart export failed: {str(e)}")
    
    async def export_multiple_formats(
        self,
        data: pd.DataFrame,
        formats: List[str],
        base_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export data to multiple formats simultaneously"""
        try:
            if not base_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"data_export_{timestamp}"
            
            exports = {}
            
            for format in formats:
                try:
                    if format == ExportFormat.CSV:
                        result = await self.export_data_to_csv(data, f"{base_filename}.csv")
                    elif format == ExportFormat.EXCEL:
                        result = await self.export_data_to_excel(data, f"{base_filename}.xlsx")
                    elif format == ExportFormat.JSON:
                        result = await self.export_data_to_json(data, f"{base_filename}.json")
                    else:
                        continue
                    
                    exports[format] = result
                    
                except Exception as e:
                    logger.error(f"Failed to export to {format}: {str(e)}")
                    exports[format] = {'error': str(e)}
            
            return {
                'base_filename': base_filename,
                'successful_exports': len([e for e in exports.values() if 'error' not in e]),
                'total_formats': len(formats),
                'exports': exports,
                'metadata': {
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'data_shape': data.shape
                }
            }
            
        except Exception as e:
            logger.error(f"Multiple format export failed: {str(e)}")
            raise Exception(f"Multiple format export failed: {str(e)}")
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for pandas/numpy objects"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        elif isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        
        return str(obj)
    
    async def get_export_capabilities(self) -> Dict[str, Any]:
        """Get available export formats and their capabilities"""
        return {
            'supported_formats': {
                ExportFormat.CSV: {
                    'description': 'Comma-separated values',
                    'extensions': ['.csv'],
                    'features': ['custom_separator', 'custom_headers', 'date_formatting'],
                    'max_rows': self.max_export_rows
                },
                ExportFormat.EXCEL: {
                    'description': 'Microsoft Excel format',
                    'extensions': ['.xlsx', '.xls'],
                    'features': ['multiple_sheets', 'auto_formatting', 'column_sizing'],
                    'max_rows': self.max_export_rows
                },
                ExportFormat.JSON: {
                    'description': 'JavaScript Object Notation',
                    'extensions': ['.json'],
                    'features': ['multiple_formats', 'metadata_inclusion', 'nested_structures'],
                    'max_rows': self.max_export_rows
                }
            },
            'chart_export_formats': {
                ExportFormat.PNG: {
                    'description': 'Portable Network Graphics',
                    'chart_types': ['line', 'bar', 'scatter', 'histogram', 'heatmap', 'interactive_*']
                },
                ExportFormat.SVG: {
                    'description': 'Scalable Vector Graphics', 
                    'chart_types': ['interactive_line', 'interactive_bar', 'interactive_scatter']
                },
                ExportFormat.HTML: {
                    'description': 'Interactive HTML with Plotly',
                    'chart_types': ['interactive_line', 'interactive_bar', 'interactive_scatter']
                }
            },
            'limitations': {
                'max_export_rows': self.max_export_rows,
                'max_file_size_mb': 100,
                'supported_data_types': ['numeric', 'text', 'datetime', 'boolean']
            }
        }