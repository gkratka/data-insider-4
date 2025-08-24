from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union


class FilterCondition(BaseModel):
    column: str
    operator: str  # equals, not_equals, greater_than, less_than, contains, not_null, is_null
    value: Optional[Union[str, int, float]] = None


class AggregationRequest(BaseModel):
    group_by: List[str]
    aggregations: Dict[str, str]  # column -> function (sum, mean, count, etc.)


class SortColumn(BaseModel):
    column: str
    ascending: bool = True


class DataQuery(BaseModel):
    file_id: int
    filters: Optional[List[FilterCondition]] = None
    aggregation: Optional[AggregationRequest] = None
    sort_columns: Optional[List[SortColumn]] = None
    limit: Optional[int] = None


class DataSummaryResponse(BaseModel):
    shape: List[int]
    columns: List[str]
    dtypes: Dict[str, str]
    memory_usage: int
    missing_values: Dict[str, int]
    duplicates: int
    numeric_stats: Optional[Dict[str, Dict[str, float]]] = None
    categorical_stats: Optional[Dict[str, Dict[str, Any]]] = None


class ColumnInfo(BaseModel):
    name: str
    type: str


class DataPreviewResponse(BaseModel):
    data: List[Dict[str, Any]]
    columns: List[ColumnInfo]
    total_rows: int
    sample_rows: int


class DataOperationResponse(BaseModel):
    success: bool
    result_data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[ColumnInfo]] = None
    total_rows: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None