from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class DescriptiveStatsRequest(BaseModel):
    """Request schema for descriptive statistics."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier") 
    columns: Optional[List[str]] = Field(None, description="Specific columns to analyze (all if None)")

class RegressionRequest(BaseModel):
    """Request schema for regression analysis."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    target_column: str = Field(..., description="Target variable column name")
    feature_columns: Optional[List[str]] = Field(None, description="Feature columns (auto-selected if None)")

class ClusteringRequest(BaseModel):
    """Request schema for clustering analysis."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    columns: Optional[List[str]] = Field(None, description="Columns to use for clustering (numeric columns if None)")
    n_clusters: int = Field(3, ge=2, le=20, description="Number of clusters (2-20)")
    method: Literal["kmeans", "hierarchical"] = Field("kmeans", description="Clustering algorithm")

class StatisticalTestRequest(BaseModel):
    """Request schema for statistical tests."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    test_type: Literal["correlation", "t_test", "chi_square"] = Field(..., description="Type of statistical test")
    parameters: Dict[str, Any] = Field(..., description="Test-specific parameters")

class VisualizationRequest(BaseModel):
    """Request schema for statistical visualizations."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    chart_type: Literal["correlation_heatmap", "distribution", "scatter"] = Field(..., description="Type of chart")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Chart-specific parameters")

# Response schemas
class DescriptiveStatsResponse(BaseModel):
    """Response schema for descriptive statistics."""
    status: str
    file_id: str
    session_id: str
    statistics: Dict[str, Any]

class RegressionResponse(BaseModel):
    """Response schema for regression analysis."""
    status: str
    file_id: str
    session_id: str
    analysis: Dict[str, Any]

class ClusteringResponse(BaseModel):
    """Response schema for clustering analysis."""
    status: str
    file_id: str
    session_id: str
    analysis: Dict[str, Any]

class StatisticalTestResponse(BaseModel):
    """Response schema for statistical tests."""
    status: str
    file_id: str
    session_id: str
    test_result: Dict[str, Any]

class VisualizationResponse(BaseModel):
    """Response schema for visualizations."""
    status: str
    file_id: str
    session_id: str
    chart_type: str
    image: str

class AnalysisSummaryResponse(BaseModel):
    """Response schema for analysis summary."""
    status: str
    file_id: str
    session_id: str
    summary: Dict[str, Any]

# Advanced analysis models
class DataQualityMetrics(BaseModel):
    """Data quality assessment metrics."""
    completeness_score: float = Field(ge=0, le=100, description="Percentage of complete data")
    consistency_score: float = Field(ge=0, le=100, description="Data consistency score") 
    accuracy_indicators: Dict[str, Any] = Field(default_factory=dict, description="Data accuracy indicators")
    missing_data_analysis: Dict[str, Any] = Field(default_factory=dict, description="Missing data patterns")

class StatisticalInsights(BaseModel):
    """Statistical insights and patterns."""
    correlation_insights: List[Dict[str, Any]] = Field(default_factory=list, description="Key correlation findings")
    distribution_insights: List[Dict[str, Any]] = Field(default_factory=list, description="Distribution patterns")
    outlier_analysis: Dict[str, Any] = Field(default_factory=dict, description="Outlier detection results")
    trend_analysis: Optional[Dict[str, Any]] = Field(None, description="Time series trend analysis if applicable")

class ModelRecommendations(BaseModel):
    """ML model recommendations based on data analysis."""
    recommended_models: List[str] = Field(default_factory=list, description="Recommended ML algorithms")
    feature_engineering_suggestions: List[str] = Field(default_factory=list, description="Feature engineering recommendations")
    preprocessing_steps: List[str] = Field(default_factory=list, description="Recommended preprocessing steps")
    potential_challenges: List[str] = Field(default_factory=list, description="Potential modeling challenges")

class ComprehensiveAnalysis(BaseModel):
    """Comprehensive analysis results."""
    data_overview: Dict[str, Any]
    data_quality: DataQualityMetrics
    statistical_insights: StatisticalInsights
    model_recommendations: ModelRecommendations
    analysis_timestamp: str
    computation_time: float

# Error schemas
class StatisticsError(BaseModel):
    """Error response schema for statistics endpoints."""
    error: str
    details: Optional[str] = None
    suggestions: Optional[List[str]] = None

# Batch processing schemas
class BatchAnalysisRequest(BaseModel):
    """Request schema for batch statistical analysis."""
    session_id: str = Field(..., description="Session identifier")
    file_ids: List[str] = Field(..., min_items=1, description="List of file identifiers")
    analysis_types: List[Literal["descriptive", "correlation", "clustering"]] = Field(
        ..., min_items=1, description="Types of analysis to perform"
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Common parameters for all analyses")

class BatchAnalysisResponse(BaseModel):
    """Response schema for batch statistical analysis."""
    status: str
    session_id: str
    results: List[Dict[str, Any]]
    execution_time: float
    failed_analyses: List[Dict[str, str]] = Field(default_factory=list, description="Failed analysis details")

# Model performance schemas
class ModelPerformanceMetrics(BaseModel):
    """Model performance metrics."""
    model_type: str
    training_score: float
    validation_score: float
    test_score: Optional[float] = None
    cross_validation_scores: Optional[List[float]] = None
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    confusion_matrix: Optional[List[List[int]]] = None
    classification_report: Optional[Dict[str, Any]] = None

class ModelComparisonRequest(BaseModel):
    """Request schema for model comparison."""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    target_column: str = Field(..., description="Target variable column name")
    model_types: List[Literal["linear_regression", "logistic_regression", "random_forest", "svm"]] = Field(
        ..., min_items=2, description="Models to compare"
    )
    feature_columns: Optional[List[str]] = Field(None, description="Feature columns")
    cross_validation_folds: int = Field(5, ge=3, le=10, description="Number of CV folds")

class ModelComparisonResponse(BaseModel):
    """Response schema for model comparison."""
    status: str
    file_id: str
    session_id: str
    target_column: str
    model_performances: List[ModelPerformanceMetrics]
    best_model: str
    comparison_summary: Dict[str, Any]