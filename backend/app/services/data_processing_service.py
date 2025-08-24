import pandas as pd
import numpy as np
import json
import io
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import logging

from app.models.file import UploadedFile


logger = logging.getLogger(__name__)


class DataProcessingEngine:
    """Core data processing engine using pandas"""
    
    def __init__(self):
        self.supported_formats = {
            'csv': self._load_csv,
            'excel': self._load_excel,
            'json': self._load_json,
            'parquet': self._load_parquet
        }
        self.data_cache = {}  # In-memory cache for small datasets
    
    async def load_file_data(self, file_record: UploadedFile) -> pd.DataFrame:
        """
        Load data from uploaded file into pandas DataFrame
        
        Args:
            file_record: Database record of uploaded file
            
        Returns:
            pandas DataFrame with loaded data
        """
        cache_key = f"file_{file_record.id}"
        
        # Check cache first
        if cache_key in self.data_cache:
            logger.info(f"Loading data from cache for file {file_record.id}")
            return self.data_cache[cache_key]
        
        if file_record.file_type not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {file_record.file_type}")
        
        try:
            loader_func = self.supported_formats[file_record.file_type]
            df = await loader_func(file_record.file_path)
            
            # Cache small datasets (< 50MB in memory)
            if df.memory_usage(deep=True).sum() < 50 * 1024 * 1024:
                self.data_cache[cache_key] = df
                logger.info(f"Cached data for file {file_record.id}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to load data from file {file_record.id}: {str(e)}")
            raise ValueError(f"Failed to load data: {str(e)}")
    
    async def _load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with automatic encoding detection"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                logger.info(f"Successfully loaded CSV with {encoding} encoding")
                return self._clean_dataframe(df)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == encodings[-1]:  # Last encoding attempt
                    raise e
                continue
        
        raise ValueError("Could not decode CSV file with any supported encoding")
    
    async def _load_excel(self, file_path: str) -> pd.DataFrame:
        """Load Excel file"""
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            return self._clean_dataframe(df)
        except Exception as e:
            logger.error(f"Failed to load Excel file: {str(e)}")
            raise ValueError(f"Failed to load Excel file: {str(e)}")
    
    async def _load_json(self, file_path: str) -> pd.DataFrame:
        """Load JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("JSON must be an object or array of objects")
            
            return self._clean_dataframe(df)
            
        except Exception as e:
            logger.error(f"Failed to load JSON file: {str(e)}")
            raise ValueError(f"Failed to load JSON file: {str(e)}")
    
    async def _load_parquet(self, file_path: str) -> pd.DataFrame:
        """Load Parquet file"""
        try:
            df = pd.read_parquet(file_path)
            return self._clean_dataframe(df)
        except Exception as e:
            logger.error(f"Failed to load Parquet file: {str(e)}")
            raise ValueError(f"Failed to load Parquet file: {str(e)}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform basic data cleaning on DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Clean column names
        df.columns = df.columns.astype(str)
        df.columns = [col.strip() for col in df.columns]
        
        # Auto-detect and convert data types
        df = self._auto_convert_types(df)
        
        return df
    
    def _auto_convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Automatically convert data types for better performance
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with optimized types
        """
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
                
                # Try to convert to datetime
                if df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_datetime(df[col], errors='ignore', infer_datetime_format=True)
                    except:
                        pass
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive summary of DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dict with data summary
        """
        summary = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': int(df.duplicated().sum())
        }
        
        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['numeric_stats'] = df[numeric_cols].describe().to_dict()
        
        # Categorical columns info
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            summary['categorical_stats'] = {}
            for col in categorical_cols:
                unique_count = df[col].nunique()
                if unique_count <= 20:  # Only show value counts for low cardinality
                    summary['categorical_stats'][col] = {
                        'unique_count': unique_count,
                        'value_counts': df[col].value_counts().head(10).to_dict()
                    }
                else:
                    summary['categorical_stats'][col] = {
                        'unique_count': unique_count
                    }
        
        return summary
    
    def filter_data(self, df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Apply filters to DataFrame
        
        Args:
            df: Input DataFrame
            filters: List of filter conditions
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        for filter_condition in filters:
            column = filter_condition.get('column')
            operator = filter_condition.get('operator')
            value = filter_condition.get('value')
            
            if column not in df.columns:
                continue
            
            if operator == 'equals':
                filtered_df = filtered_df[filtered_df[column] == value]
            elif operator == 'not_equals':
                filtered_df = filtered_df[filtered_df[column] != value]
            elif operator == 'greater_than':
                filtered_df = filtered_df[filtered_df[column] > value]
            elif operator == 'less_than':
                filtered_df = filtered_df[filtered_df[column] < value]
            elif operator == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value), na=False)]
            elif operator == 'not_null':
                filtered_df = filtered_df[filtered_df[column].notna()]
            elif operator == 'is_null':
                filtered_df = filtered_df[filtered_df[column].isna()]
        
        return filtered_df
    
    def aggregate_data(self, df: pd.DataFrame, group_by: List[str], aggregations: Dict[str, str]) -> pd.DataFrame:
        """
        Perform group by aggregations
        
        Args:
            df: Input DataFrame
            group_by: Columns to group by
            aggregations: Dict of column -> aggregation function
            
        Returns:
            Aggregated DataFrame
        """
        try:
            # Validate group by columns exist
            missing_cols = [col for col in group_by if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Group by columns not found: {missing_cols}")
            
            # Validate aggregation columns exist
            missing_agg_cols = [col for col in aggregations.keys() if col not in df.columns]
            if missing_agg_cols:
                raise ValueError(f"Aggregation columns not found: {missing_agg_cols}")
            
            grouped = df.groupby(group_by)
            result = grouped.agg(aggregations).reset_index()
            
            return result
            
        except Exception as e:
            logger.error(f"Aggregation failed: {str(e)}")
            raise ValueError(f"Aggregation failed: {str(e)}")
    
    def sort_data(self, df: pd.DataFrame, sort_columns: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Sort DataFrame by specified columns
        
        Args:
            df: Input DataFrame  
            sort_columns: List of dicts with 'column' and 'ascending' keys
            
        Returns:
            Sorted DataFrame
        """
        columns = []
        ascending = []
        
        for sort_col in sort_columns:
            col_name = sort_col.get('column')
            if col_name in df.columns:
                columns.append(col_name)
                ascending.append(sort_col.get('ascending', True))
        
        if columns:
            return df.sort_values(by=columns, ascending=ascending)
        else:
            return df
    
    def get_sample_data(self, df: pd.DataFrame, n_rows: int = 100) -> Dict[str, Any]:
        """
        Get sample of data for preview
        
        Args:
            df: Input DataFrame
            n_rows: Number of rows to sample
            
        Returns:
            Dict with sample data and metadata
        """
        sample_df = df.head(n_rows)
        
        return {
            'data': sample_df.to_dict('records'),
            'columns': [{'name': col, 'type': str(df[col].dtype)} for col in df.columns],
            'total_rows': len(df),
            'sample_rows': len(sample_df)
        }
    
    def clear_cache(self, file_id: Optional[int] = None):
        """Clear data cache"""
        if file_id:
            cache_key = f"file_{file_id}"
            if cache_key in self.data_cache:
                del self.data_cache[cache_key]
        else:
            self.data_cache.clear()


# Global instance
data_processing_engine = DataProcessingEngine()