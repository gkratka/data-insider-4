from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class MultiTableJoinRequest(BaseModel):
    """Request schema for multi-table join operations."""
    session_id: str = Field(..., description="Session identifier")
    file_ids: List[str] = Field(..., min_items=2, description="List of file identifiers to join")
    query: str = Field(..., description="Natural language query describing the join operation")
    join_keys: Optional[Dict[str, str]] = Field(None, description="Explicit join keys mapping")
    join_type: Optional[Literal["inner", "left", "right", "outer", "cross"]] = Field("inner", description="Type of join to perform")

class ComplexAggregationRequest(BaseModel):
    """Request schema for complex aggregation operations."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    query: str = Field(..., description="Natural language query for aggregation")
    group_columns: Optional[List[str]] = Field(None, description="Columns to group by")
    agg_functions: Optional[Dict[str, List[str]]] = Field(None, description="Aggregation functions per column")

class TimeSeriesAnalysisRequest(BaseModel):
    """Request schema for time series analysis."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    query: str = Field(..., description="Natural language query for time series analysis")
    date_column: Optional[str] = Field(None, description="Date/time column name")
    value_columns: Optional[List[str]] = Field(None, description="Value columns for analysis")
    operation: Optional[Literal["trend", "seasonality", "moving_average", "growth_rate", "forecast", "anomaly"]] = Field(None, description="Specific time series operation")

class QueryOptimizationRequest(BaseModel):
    """Request schema for query optimization analysis."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    query: str = Field(..., description="Query to optimize")
    execution_time: Optional[float] = Field(None, description="Current execution time in seconds")