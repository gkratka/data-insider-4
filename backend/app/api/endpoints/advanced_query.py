from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from app.services.advanced_query_processor import (
    AdvancedQueryProcessor, JoinType, TimeSeriesOperation
)
from app.services.data_processing_service import DataProcessingService
from app.services.session_service import SessionService
from app.services.file_service import FileService
from app.schemas.advanced_query import (
    MultiTableJoinRequest,
    ComplexAggregationRequest,
    TimeSeriesAnalysisRequest,
    QueryOptimizationRequest
)

router = APIRouter(prefix="/advanced-query", tags=["advanced-query"])


@router.post("/multi-table-join")
async def multi_table_join(
    request: MultiTableJoinRequest,
    advanced_processor: AdvancedQueryProcessor = Depends(AdvancedQueryProcessor),
    session_service: SessionService = Depends(SessionService),
    file_service: FileService = Depends(FileService)
) -> Dict[str, Any]:
    """Execute multi-table join operations"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file records
        file_records = []
        for file_id in request.file_ids:
            file_record = file_service.get_file_by_id(None, file_id)  # TODO: Add proper DB session
            if not file_record:
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
            file_records.append(file_record)
        
        # Process multi-table join
        result = await advanced_processor.process_multi_table_join(
            query=request.query,
            file_records=file_records,
            session_id=request.session_id,
            join_keys=request.join_keys,
            join_type=JoinType(request.join_type) if request.join_type else JoinType.INNER
        )
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "file_ids": request.file_ids,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-table join failed: {str(e)}")


@router.post("/complex-aggregation") 
async def complex_aggregation(
    request: ComplexAggregationRequest,
    advanced_processor: AdvancedQueryProcessor = Depends(AdvancedQueryProcessor),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Execute complex aggregation operations"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Process complex aggregation
        result = await advanced_processor.process_complex_aggregation(
            query=request.query,
            df=df,
            group_columns=request.group_columns,
            agg_functions=request.agg_functions
        )
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complex aggregation failed: {str(e)}")


@router.post("/time-series-analysis")
async def time_series_analysis(
    request: TimeSeriesAnalysisRequest,
    advanced_processor: AdvancedQueryProcessor = Depends(AdvancedQueryProcessor),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Execute time series analysis operations"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Process time series analysis
        result = await advanced_processor.process_time_series_analysis(
            query=request.query,
            df=df,
            date_column=request.date_column,
            value_columns=request.value_columns,
            operation=TimeSeriesOperation(request.operation) if request.operation else None
        )
        
        return {
            "status": "success", 
            "file_id": request.file_id,
            "session_id": request.session_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Time series analysis failed: {str(e)}")


@router.post("/query-optimization")
async def query_optimization(
    request: QueryOptimizationRequest,
    advanced_processor: AdvancedQueryProcessor = Depends(AdvancedQueryProcessor),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Generate query optimization recommendations"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Generate optimization recommendations
        result = await advanced_processor.generate_query_optimization_recommendations(
            query=request.query,
            df=df,
            execution_time=request.execution_time
        )
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query optimization failed: {str(e)}")


@router.get("/capabilities")
async def get_advanced_capabilities() -> Dict[str, Any]:
    """Get available advanced query processing capabilities"""
    return {
        "multi_table_operations": {
            "join_types": ["inner", "left", "right", "outer", "cross"],
            "supported_operations": ["merge", "join", "combine", "relate"],
            "auto_key_detection": True,
            "max_tables": 10
        },
        "complex_aggregations": {
            "supported_functions": [
                "sum", "mean", "count", "min", "max", "std", "var",
                "quantile", "nunique", "first", "last", "size"
            ],
            "grouping_operations": ["single", "multiple", "hierarchical"],
            "advanced_functions": ["rolling", "expanding", "resample"]
        },
        "time_series_analysis": {
            "operations": [
                "trend_analysis", "seasonality", "moving_average", 
                "growth_rate", "forecast", "anomaly_detection"
            ],
            "date_formats": [
                "YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY",
                "Mon DD, YYYY", "DD Mon YYYY"
            ],
            "window_functions": ["rolling", "expanding", "exponential"]
        },
        "optimization_features": {
            "performance_analysis": True,
            "memory_optimization": True,
            "query_rewriting": True,
            "index_recommendations": True,
            "chunking_strategies": True
        },
        "supported_data_types": {
            "numeric": ["int", "float", "decimal"],
            "temporal": ["datetime", "date", "time", "timestamp"],
            "categorical": ["string", "category", "boolean"],
            "advanced": ["json", "array", "nested"]
        }
    }


@router.post("/validate-query")
async def validate_advanced_query(
    query: str,
    file_id: str,
    session_id: str,
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Validate advanced query syntax and feasibility"""
    try:
        # Validate session
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data summary
        df = await data_service.get_file_data(file_id, session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Analyze query
        validation_results = {
            "is_valid": True,
            "query_type": "advanced",
            "estimated_complexity": "medium",
            "warnings": [],
            "suggestions": [],
            "estimated_execution_time": "< 5 seconds",
            "memory_requirements": "standard"
        }
        
        query_lower = query.lower()
        
        # Check for complex operations
        if any(op in query_lower for op in ["join", "merge", "combine"]):
            validation_results["query_type"] = "multi_table_join"
            validation_results["estimated_complexity"] = "high"
        
        if any(op in query_lower for op in ["group by", "aggregate", "sum", "mean"]):
            validation_results["query_type"] = "aggregation"
            
        if any(op in query_lower for op in ["time", "date", "trend", "forecast"]):
            validation_results["query_type"] = "time_series"
        
        # Performance warnings
        if len(df) > 100000:
            validation_results["warnings"].append("Large dataset detected - consider chunking for better performance")
            validation_results["estimated_execution_time"] = "5-30 seconds"
        
        if len(df.columns) > 50:
            validation_results["warnings"].append("Many columns detected - specify columns explicitly for better performance")
        
        # Suggestions
        if "join" in query_lower and len(df) > 50000:
            validation_results["suggestions"].append("Consider indexing join keys for better performance")
        
        if any(agg in query_lower for agg in ["sum", "mean", "count"]) and len(df) > 10000:
            validation_results["suggestions"].append("Use categorical data types for grouping columns")
        
        return {
            "status": "success",
            "query": query,
            "file_id": file_id,
            "session_id": session_id,
            "validation": validation_results,
            "dataset_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "size_mb": df.memory_usage(deep=True).sum() / 1024**2,
                "column_types": df.dtypes.value_counts().to_dict()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query validation failed: {str(e)}")


@router.get("/query-templates")
async def get_query_templates() -> Dict[str, Any]:
    """Get templates for advanced query operations"""
    return {
        "multi_table_join": {
            "inner_join": "Join customers and orders on customer_id",
            "left_join": "Get all customers with their orders (including customers without orders)",
            "aggregate_join": "Show total sales per customer by joining orders and customers"
        },
        "complex_aggregation": {
            "multiple_grouping": "Group sales by region and category, show sum and average",
            "rolling_aggregation": "Calculate 30-day rolling average of daily sales",
            "percentile_analysis": "Show 25th, 50th, and 75th percentiles by category"
        },
        "time_series_analysis": {
            "trend_analysis": "Show sales trend over the last 12 months",
            "seasonality": "Identify seasonal patterns in monthly revenue",
            "growth_rate": "Calculate month-over-month growth rate",
            "moving_average": "Show 7-day moving average of daily transactions"
        },
        "window_functions": {
            "ranking": "Rank products by sales within each category",
            "lag_lead": "Compare current month sales with previous month",
            "cumulative": "Show running total of sales by date"
        }
    }