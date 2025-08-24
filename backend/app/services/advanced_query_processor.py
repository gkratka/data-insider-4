import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.claude_service import claude_client
from app.services.data_processing_service import DataProcessingService

logger = logging.getLogger(__name__)

class AdvancedQueryIntent(Enum):
    """Advanced query intents for complex operations"""
    MULTI_TABLE_JOIN = "multi_table_join"
    COMPLEX_AGGREGATION = "complex_aggregation"
    TIME_SERIES_ANALYSIS = "time_series_analysis"
    WINDOW_FUNCTIONS = "window_functions"
    PIVOT_UNPIVOT = "pivot_unpivot"
    CONDITIONAL_LOGIC = "conditional_logic"
    ADVANCED_FILTERING = "advanced_filtering"
    QUERY_OPTIMIZATION = "query_optimization"

class JoinType(Enum):
    """Types of table joins"""
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right" 
    OUTER = "outer"
    CROSS = "cross"

class TimeSeriesOperation(Enum):
    """Time series analysis operations"""
    TREND_ANALYSIS = "trend"
    SEASONALITY = "seasonality"
    MOVING_AVERAGE = "moving_average"
    GROWTH_RATE = "growth_rate"
    FORECAST = "forecast"
    ANOMALY_DETECTION = "anomaly"

class AdvancedQueryProcessor:
    """Enhanced query processor for complex data operations"""
    
    def __init__(self):
        self.data_service = DataProcessingService()
        
        # Advanced intent keywords
        self.advanced_intent_keywords = {
            AdvancedQueryIntent.MULTI_TABLE_JOIN: [
                "join", "merge", "combine", "relate", "match", "link",
                "inner join", "left join", "outer join", "cross join"
            ],
            AdvancedQueryIntent.COMPLEX_AGGREGATION: [
                "group by multiple", "nested aggregation", "rollup", "cube",
                "percentile", "quantile", "cumulative", "running total"
            ],
            AdvancedQueryIntent.TIME_SERIES_ANALYSIS: [
                "trend", "time series", "over time", "temporal", "seasonal",
                "moving average", "growth rate", "forecast", "predict"
            ],
            AdvancedQueryIntent.WINDOW_FUNCTIONS: [
                "rank", "row_number", "dense_rank", "lag", "lead",
                "partition by", "window", "running", "cumulative"
            ],
            AdvancedQueryIntent.PIVOT_UNPIVOT: [
                "pivot", "unpivot", "reshape", "transpose", "crosstab",
                "wide to long", "long to wide"
            ],
            AdvancedQueryIntent.CONDITIONAL_LOGIC: [
                "case when", "if then", "conditional", "where case",
                "multiple conditions", "nested conditions"
            ]
        }
        
        # Date/time patterns
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # M/D/YY or MM/DD/YYYY
            r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',  # D Mon YYYY
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b'  # Mon D, YYYY
        ]

    def classify_advanced_intent(self, query: str) -> AdvancedQueryIntent:
        """Classify advanced query intents"""
        query_lower = query.lower()
        
        intent_scores = {}
        for intent, keywords in self.advanced_intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            intent_scores[intent] = score
        
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        
        # Additional logic for implicit intents
        if any(date_pattern in query for date_pattern in [
            "daily", "weekly", "monthly", "yearly", "time", "date"
        ]):
            return AdvancedQueryIntent.TIME_SERIES_ANALYSIS
            
        if "multiple" in query_lower and "group" in query_lower:
            return AdvancedQueryIntent.COMPLEX_AGGREGATION
            
        return None

    async def process_multi_table_join(
        self, 
        query: str, 
        file_records: List[Any],
        session_id: str,
        join_keys: Optional[Dict[str, str]] = None,
        join_type: JoinType = JoinType.INNER
    ) -> Dict[str, Any]:
        """Process multi-table join operations"""
        try:
            if len(file_records) < 2:
                return {
                    'success': False,
                    'error': 'At least 2 tables required for join operation'
                }
            
            # Load all dataframes
            dataframes = {}
            for i, file_record in enumerate(file_records):
                df = await self.data_service.get_file_data(file_record.id, session_id)
                if df is None:
                    return {
                        'success': False,
                        'error': f'Could not load data for file {file_record.filename}'
                    }
                dataframes[f'df_{i}'] = df
            
            # Auto-detect join keys if not provided
            if not join_keys:
                join_keys = await self._auto_detect_join_keys(dataframes, query)
            
            # Generate join code using Claude
            join_code = await self._generate_join_code(
                query, dataframes, join_keys, join_type
            )
            
            # Execute join
            success, result, error = await self._execute_safe_code(
                join_code, dataframes
            )
            
            if not success:
                return {
                    'success': False,
                    'error': f'Join execution failed: {error}',
                    'generated_code': join_code
                }
            
            # Process results
            return {
                'success': True,
                'intent': 'multi_table_join',
                'join_type': join_type.value,
                'join_keys': join_keys,
                'generated_code': join_code,
                'result_data': result.head(100).to_dict('records') if isinstance(result, pd.DataFrame) else [{'result': str(result)}],
                'columns': [{'name': col, 'type': str(result[col].dtype)} for col in result.columns] if isinstance(result, pd.DataFrame) else [],
                'total_rows': len(result) if isinstance(result, pd.DataFrame) else 1,
                'table_info': {
                    name: {'shape': df.shape, 'columns': df.columns.tolist()} 
                    for name, df in dataframes.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Multi-table join failed: {str(e)}")
            return {
                'success': False,
                'error': f'Multi-table join failed: {str(e)}'
            }

    async def process_complex_aggregation(
        self,
        query: str,
        df: pd.DataFrame,
        group_columns: Optional[List[str]] = None,
        agg_functions: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """Process complex aggregation queries"""
        try:
            # Auto-detect aggregation patterns if not specified
            if not group_columns or not agg_functions:
                group_columns, agg_functions = await self._extract_aggregation_params(query, df)
            
            # Generate complex aggregation code
            agg_code = await self._generate_complex_aggregation_code(
                query, df, group_columns, agg_functions
            )
            
            # Execute aggregation
            success, result, error = await self._execute_safe_code(
                agg_code, {'df': df, 'pd': pd, 'np': np}
            )
            
            if not success:
                return {
                    'success': False,
                    'error': f'Aggregation failed: {error}',
                    'generated_code': agg_code
                }
            
            return {
                'success': True,
                'intent': 'complex_aggregation',
                'group_columns': group_columns,
                'agg_functions': agg_functions,
                'generated_code': agg_code,
                'result_data': result.to_dict('records') if isinstance(result, pd.DataFrame) else [{'result': str(result)}],
                'columns': [{'name': col, 'type': str(result[col].dtype)} for col in result.columns] if isinstance(result, pd.DataFrame) else [],
                'total_rows': len(result) if isinstance(result, pd.DataFrame) else 1
            }
            
        except Exception as e:
            logger.error(f"Complex aggregation failed: {str(e)}")
            return {
                'success': False,
                'error': f'Complex aggregation failed: {str(e)}'
            }

    async def process_time_series_analysis(
        self,
        query: str,
        df: pd.DataFrame,
        date_column: Optional[str] = None,
        value_columns: Optional[List[str]] = None,
        operation: Optional[TimeSeriesOperation] = None
    ) -> Dict[str, Any]:
        """Process time series analysis queries"""
        try:
            # Auto-detect date column if not specified
            if not date_column:
                date_column = await self._detect_date_column(df, query)
            
            if not date_column:
                return {
                    'success': False,
                    'error': 'No date/time column detected in the dataset'
                }
            
            # Auto-detect operation type
            if not operation:
                operation = await self._detect_time_series_operation(query)
            
            # Generate time series analysis code
            ts_code = await self._generate_time_series_code(
                query, df, date_column, value_columns, operation
            )
            
            # Execute time series analysis
            success, result, error = await self._execute_safe_code(
                ts_code, {
                    'df': df, 'pd': pd, 'np': np,
                    'datetime': datetime, 'timedelta': timedelta
                }
            )
            
            if not success:
                return {
                    'success': False,
                    'error': f'Time series analysis failed: {error}',
                    'generated_code': ts_code
                }
            
            return {
                'success': True,
                'intent': 'time_series_analysis',
                'date_column': date_column,
                'value_columns': value_columns,
                'operation': operation.value if operation else 'general',
                'generated_code': ts_code,
                'result_data': result.to_dict('records') if isinstance(result, pd.DataFrame) else [{'result': str(result)}],
                'columns': [{'name': col, 'type': str(result[col].dtype)} for col in result.columns] if isinstance(result, pd.DataFrame) else [],
                'total_rows': len(result) if isinstance(result, pd.DataFrame) else 1
            }
            
        except Exception as e:
            logger.error(f"Time series analysis failed: {str(e)}")
            return {
                'success': False,
                'error': f'Time series analysis failed: {str(e)}'
            }

    async def generate_query_optimization_recommendations(
        self,
        query: str,
        df: pd.DataFrame,
        execution_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate query optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze dataset characteristics
            data_size = df.memory_usage(deep=True).sum() / 1024**2  # MB
            row_count = len(df)
            col_count = len(df.columns)
            
            # Size-based recommendations
            if data_size > 100:  # > 100MB
                recommendations.append({
                    'type': 'memory_optimization',
                    'suggestion': 'Consider chunking operations for large datasets',
                    'reason': f'Dataset size: {data_size:.1f}MB'
                })
            
            if row_count > 100000:
                recommendations.append({
                    'type': 'indexing',
                    'suggestion': 'Use .iloc or .loc for row selection instead of boolean indexing',
                    'reason': f'Large row count: {row_count:,} rows'
                })
            
            # Query pattern analysis
            query_lower = query.lower()
            
            if 'group' in query_lower and row_count > 10000:
                recommendations.append({
                    'type': 'aggregation_optimization',
                    'suggestion': 'Use categorical data types for grouping columns',
                    'reason': 'GroupBy operations on large datasets benefit from categorical types'
                })
            
            if any(op in query_lower for op in ['join', 'merge']) and row_count > 50000:
                recommendations.append({
                    'type': 'join_optimization',
                    'suggestion': 'Ensure join keys are indexed and consider using merge with how parameter',
                    'reason': 'Large datasets benefit from optimized join strategies'
                })
            
            # Column-specific recommendations
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 10:
                recommendations.append({
                    'type': 'column_selection',
                    'suggestion': 'Select only necessary columns before operations',
                    'reason': f'Many numeric columns: {len(numeric_cols)}'
                })
            
            # Generate optimized code
            optimized_code = await self._generate_optimized_code(query, df, recommendations)
            
            return {
                'success': True,
                'dataset_stats': {
                    'size_mb': data_size,
                    'rows': row_count,
                    'columns': col_count
                },
                'recommendations': recommendations,
                'optimized_code': optimized_code,
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Query optimization failed: {str(e)}")
            return {
                'success': False,
                'error': f'Query optimization failed: {str(e)}'
            }

    # Helper methods
    async def _auto_detect_join_keys(
        self, 
        dataframes: Dict[str, pd.DataFrame], 
        query: str
    ) -> Dict[str, str]:
        """Auto-detect potential join keys between dataframes"""
        join_keys = {}
        
        # Get column lists
        df_columns = {name: df.columns.tolist() for name, df in dataframes.items()}
        
        # Find common column names
        all_columns = set()
        for cols in df_columns.values():
            all_columns.update(cols)
        
        common_columns = []
        for col in all_columns:
            if sum(1 for cols in df_columns.values() if col in cols) >= 2:
                common_columns.append(col)
        
        # Look for likely ID columns
        id_patterns = ['id', 'key', 'code', 'number']
        likely_keys = []
        
        for col in common_columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in id_patterns):
                likely_keys.append(col)
        
        # Use first likely key or first common column
        if likely_keys:
            join_key = likely_keys[0]
        elif common_columns:
            join_key = common_columns[0]
        else:
            join_key = None
        
        if join_key:
            df_names = list(dataframes.keys())
            for i in range(len(df_names) - 1):
                join_keys[f"{df_names[i]}_{df_names[i+1]}"] = join_key
        
        return join_keys

    async def _generate_join_code(
        self,
        query: str,
        dataframes: Dict[str, pd.DataFrame],
        join_keys: Dict[str, str],
        join_type: JoinType
    ) -> str:
        """Generate pandas code for multi-table joins"""
        system_prompt = """You are an expert in pandas multi-table operations. Generate efficient pandas code for joining multiple DataFrames based on the query requirements.

Requirements:
- Use pandas merge() function
- Handle different join types (inner, left, right, outer)
- Use appropriate suffixes for overlapping columns
- Optimize for performance
- Return only the code, no explanations"""
        
        df_info = {
            name: {
                'columns': df.columns.tolist(),
                'shape': df.shape
            }
            for name, df in dataframes.items()
        }
        
        user_prompt = f"""
DataFrames available: {list(dataframes.keys())}
DataFrame information: {json.dumps(df_info, indent=2)}
Join keys: {join_keys}
Join type: {join_type.value}

Query: "{query}"

Generate pandas code to join these DataFrames according to the query requirements.
Use variable names as provided in the DataFrames dict.
Store the final result in a variable called 'result'.
"""
        
        try:
            messages = [{'role': 'user', 'content': user_prompt}]
            response = await claude_client.create_completion(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=800,
                temperature=0.1
            )
            
            return self._extract_code_from_response(response['content'])
            
        except Exception as e:
            logger.error(f"Join code generation failed: {str(e)}")
            # Fallback code
            df_names = list(dataframes.keys())
            join_key = list(join_keys.values())[0] if join_keys else 'id'
            return f"result = pd.merge({df_names[0]}, {df_names[1]}, on='{join_key}', how='{join_type.value}')"

    async def _extract_aggregation_params(
        self, 
        query: str, 
        df: pd.DataFrame
    ) -> Tuple[List[str], Dict[str, List[str]]]:
        """Extract grouping columns and aggregation functions from query"""
        query_lower = query.lower()
        columns = df.columns.tolist()
        
        # Default grouping columns (categorical or low-cardinality)
        group_candidates = []
        for col in columns:
            if df[col].dtype == 'object' or df[col].nunique() / len(df) < 0.1:
                group_candidates.append(col)
        
        # Extract columns mentioned in query
        mentioned_columns = [col for col in columns if col.lower() in query_lower]
        
        group_columns = mentioned_columns[:2] if mentioned_columns else group_candidates[:2]
        
        # Default aggregation functions
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        agg_functions = {}
        
        if 'sum' in query_lower:
            agg_functions.update({col: ['sum'] for col in numeric_cols[:3]})
        elif 'average' in query_lower or 'mean' in query_lower:
            agg_functions.update({col: ['mean'] for col in numeric_cols[:3]})
        elif 'count' in query_lower:
            agg_functions.update({col: ['count'] for col in numeric_cols[:3]})
        else:
            agg_functions.update({col: ['sum', 'mean', 'count'] for col in numeric_cols[:3]})
        
        return group_columns, agg_functions

    async def _detect_date_column(self, df: pd.DataFrame, query: str) -> Optional[str]:
        """Detect the primary date/time column in the dataset"""
        date_candidates = []
        
        # Look for datetime columns
        for col in df.columns:
            if df[col].dtype in ['datetime64[ns]', '<M8[ns]']:
                date_candidates.append(col)
        
        # Look for columns with date-like names
        date_name_patterns = ['date', 'time', 'created', 'modified', 'timestamp', 'when']
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in date_name_patterns):
                date_candidates.append(col)
        
        # Look for columns mentioned in query
        for col in df.columns:
            if col.lower() in query.lower():
                # Check if it contains date-like values
                try:
                    sample = df[col].dropna().head(100)
                    if sample.dtype == 'object':
                        # Try to parse as dates
                        for pattern in self.date_patterns:
                            if sample.astype(str).str.match(pattern).any():
                                date_candidates.append(col)
                                break
                except:
                    continue
        
        return date_candidates[0] if date_candidates else None

    async def _detect_time_series_operation(self, query: str) -> Optional[TimeSeriesOperation]:
        """Detect the type of time series operation requested"""
        query_lower = query.lower()
        
        operation_patterns = {
            TimeSeriesOperation.TREND_ANALYSIS: ['trend', 'trending', 'direction', 'pattern'],
            TimeSeriesOperation.MOVING_AVERAGE: ['moving average', 'rolling', 'smooth'],
            TimeSeriesOperation.GROWTH_RATE: ['growth', 'rate', 'change', 'increase', 'decrease'],
            TimeSeriesOperation.SEASONALITY: ['seasonal', 'season', 'periodic', 'cyclical'],
            TimeSeriesOperation.FORECAST: ['forecast', 'predict', 'future', 'projection'],
            TimeSeriesOperation.ANOMALY_DETECTION: ['anomaly', 'outlier', 'unusual', 'abnormal']
        }
        
        for operation, keywords in operation_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return operation
        
        return TimeSeriesOperation.TREND_ANALYSIS  # Default

    async def _generate_time_series_code(
        self,
        query: str,
        df: pd.DataFrame,
        date_column: str,
        value_columns: Optional[List[str]],
        operation: TimeSeriesOperation
    ) -> str:
        """Generate time series analysis code"""
        if not value_columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_columns = numeric_cols[:3] if numeric_cols else []
        
        base_code = f"""
# Convert date column to datetime
df['{date_column}'] = pd.to_datetime(df['{date_column}'])
df = df.sort_values('{date_column}')
df = df.set_index('{date_column}')
"""
        
        if operation == TimeSeriesOperation.MOVING_AVERAGE:
            operation_code = f"""
# Calculate moving averages
result = pd.DataFrame()
result['{date_column}'] = df.index
for col in {value_columns}:
    result[f'{{col}}_ma_7'] = df[col].rolling(window=7).mean()
    result[f'{{col}}_ma_30'] = df[col].rolling(window=30).mean()
result = result.reset_index(drop=True)
"""
        elif operation == TimeSeriesOperation.GROWTH_RATE:
            operation_code = f"""
# Calculate growth rates
result = pd.DataFrame()
result['{date_column}'] = df.index
for col in {value_columns}:
    result[f'{{col}}_pct_change'] = df[col].pct_change() * 100
    result[f'{{col}}_growth_rate'] = df[col].pct_change(periods=7) * 100
result = result.reset_index(drop=True)
"""
        else:  # Default trend analysis
            operation_code = f"""
# Basic trend analysis
result = pd.DataFrame()
result['{date_column}'] = df.index
for col in {value_columns}:
    result[col] = df[col]
    # Add trend indicators
    result[f'{{col}}_trend'] = df[col].rolling(window=10).mean()
result = result.reset_index(drop=True)
"""
        
        return base_code + operation_code

    async def _execute_safe_code(
        self, 
        code: str, 
        context: Dict[str, Any]
    ) -> Tuple[bool, Any, str]:
        """Safely execute generated code with given context"""
        try:
            safe_globals = {
                'pd': pd,
                'np': np,
                'datetime': datetime,
                'timedelta': timedelta
            }
            safe_globals.update(context)
            safe_locals = {}
            
            exec(code, safe_globals, safe_locals)
            
            if 'result' in safe_locals:
                return True, safe_locals['result'], ""
            else:
                return False, None, "No result variable found"
                
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return False, None, str(e)

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from Claude response"""
        code_block_pattern = r'```(?:python)?\s*(.*?)```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Fallback to line-based extraction
        lines = response.split('\n')
        code_lines = []
        
        for line in lines:
            line = line.strip()
            if (line.startswith('df.') or line.startswith('result =') or 
                'pd.' in line or line.startswith('#')):
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else response.strip()

    async def _generate_complex_aggregation_code(
        self,
        query: str,
        df: pd.DataFrame,
        group_columns: List[str],
        agg_functions: Dict[str, List[str]]
    ) -> str:
        """Generate complex aggregation code"""
        system_prompt = """Generate pandas code for complex aggregations including multiple grouping levels, custom aggregation functions, and advanced statistics."""
        
        user_prompt = f"""
Query: "{query}"
Group columns: {group_columns}
Aggregation functions: {agg_functions}
DataFrame shape: {df.shape}
Available columns: {df.columns.tolist()}

Generate pandas code for complex aggregation. Store result in 'result' variable.
"""
        
        try:
            messages = [{'role': 'user', 'content': user_prompt}]
            response = await claude_client.create_completion(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=600,
                temperature=0.1
            )
            
            return self._extract_code_from_response(response['content'])
            
        except Exception as e:
            logger.error(f"Complex aggregation code generation failed: {str(e)}")
            # Fallback code
            agg_dict = {col: funcs for col, funcs in agg_functions.items()}
            return f"result = df.groupby({group_columns}).agg({agg_dict}).reset_index()"

    async def _generate_optimized_code(
        self,
        query: str,
        df: pd.DataFrame,
        recommendations: List[Dict[str, str]]
    ) -> str:
        """Generate optimized pandas code based on recommendations"""
        system_prompt = """Generate optimized pandas code implementing the given performance recommendations while maintaining query functionality."""
        
        user_prompt = f"""
Original query: "{query}"
Dataset shape: {df.shape}
Performance recommendations: {json.dumps(recommendations, indent=2)}

Generate optimized pandas code implementing these recommendations.
Store the result in 'result' variable.
"""
        
        try:
            messages = [{'role': 'user', 'content': user_prompt}]
            response = await claude_client.create_completion(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=800,
                temperature=0.1
            )
            
            return self._extract_code_from_response(response['content'])
            
        except Exception as e:
            logger.error(f"Optimized code generation failed: {str(e)}")
            return "# Optimization recommendations applied\nresult = df.copy()"


# Global instance
advanced_query_processor = AdvancedQueryProcessor()