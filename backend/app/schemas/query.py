from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class NaturalLanguageQuery(BaseModel):
    query: str
    file_id: int
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    success: bool
    intent: str
    entities: Optional[Dict[str, List[str]]] = None
    generated_code: Optional[str] = None
    result_data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[Dict[str, str]]] = None
    total_rows: Optional[int] = None
    explanation: Optional[str] = None
    result_summary: Optional[str] = None
    error: Optional[str] = None


class QueryIntent(BaseModel):
    intent: str
    confidence: float
    keywords_found: List[str]


class ExtractedEntities(BaseModel):
    columns: List[str]
    values: List[str]
    operations: List[str]
    conditions: List[str]


class CodeGeneration(BaseModel):
    query: str
    intent: str
    entities: Dict[str, List[str]]
    data_summary: Dict[str, Any]


class CodeExecutionResult(BaseModel):
    success: bool
    result_type: str
    result_shape: Optional[List[int]] = None
    result_preview: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class QueryHistory(BaseModel):
    session_id: str
    queries: List[Dict[str, Any]]


class QuerySuggestion(BaseModel):
    suggestion: str
    intent: str
    description: str
    example_query: str