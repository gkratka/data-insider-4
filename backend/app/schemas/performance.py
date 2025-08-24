from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class DataOptimizationRequest(BaseModel):
    """Request schema for data optimization"""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    cache_optimized: bool = Field(False, description="Cache optimized version")

class PerformanceReportRequest(BaseModel):
    """Request schema for performance report generation"""
    include_metrics: bool = Field(True, description="Include performance metrics")
    include_recommendations: bool = Field(True, description="Include optimization recommendations")
    time_range_hours: int = Field(24, ge=1, le=168, description="Time range for metrics analysis")

class SystemResourcesResponse(BaseModel):
    """Response schema for system resources"""
    timestamp: str
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    process: Dict[str, Any]
    system_health: str

class PerformanceMetric(BaseModel):
    """Schema for individual performance metrics"""
    timestamp: str
    function: str
    execution_time: float
    memory_used_mb: float
    success: bool
    error: Optional[str] = None

class OptimizationResult(BaseModel):
    """Schema for optimization results"""
    data_type_optimizations: Dict[str, Dict[str, str]]
    duplicates_removed: int
    missing_values: int
    memory_optimization: Dict[str, float]

class PerformanceReportResponse(BaseModel):
    """Response schema for performance reports"""
    report_timestamp: str
    summary: Dict[str, Any]
    system_resources: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[List[PerformanceMetric]] = None
    database_optimizations: Optional[Dict[str, Any]] = None
    frontend_optimizations: Optional[Dict[str, Any]] = None
    actionable_recommendations: Optional[List[Dict[str, str]]] = None

class CacheStatistics(BaseModel):
    """Schema for cache statistics"""
    redis_connection: Dict[str, Any]
    cache_statistics: Dict[str, Any]
    performance_metrics: Dict[str, Any]

class OptimizationRecommendation(BaseModel):
    """Schema for optimization recommendations"""
    category: str
    priority: str
    recommendation: str
    expected_improvement: Optional[str] = None
    implementation_complexity: Optional[str] = None

class DatabaseOptimization(BaseModel):
    """Schema for database optimization recommendations"""
    recommendations: List[str]
    current_performance: Dict[str, Any]
    optimization_strategies: List[Dict[str, Any]]

class FrontendOptimization(BaseModel):
    """Schema for frontend optimization recommendations"""
    bundle_optimization: Dict[str, Any]
    react_optimizations: Dict[str, Any]
    data_fetching_optimizations: Dict[str, Any]
    metrics_to_monitor: List[str]