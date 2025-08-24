from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
import pandas as pd
from app.services.statistics_service import StatisticsService
from app.services.data_processing_service import DataProcessingService
from app.services.session_service import SessionService
from app.schemas.statistics import (
    DescriptiveStatsRequest,
    RegressionRequest,
    ClusteringRequest,
    StatisticalTestRequest,
    VisualizationRequest
)
from app.core.config import get_settings

router = APIRouter(prefix="/statistics", tags=["statistics"])
settings = get_settings()


@router.post("/descriptive")
async def get_descriptive_statistics(
    request: DescriptiveStatsRequest,
    stats_service: StatisticsService = Depends(StatisticsService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Get comprehensive descriptive statistics for a dataset."""
    try:
        # Validate session and get data
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Calculate descriptive statistics
        result = await stats_service.descriptive_statistics(df, request.columns)
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            "statistics": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating descriptive statistics: {str(e)}")


@router.post("/regression/linear")
async def linear_regression(
    request: RegressionRequest,
    stats_service: StatisticsService = Depends(StatisticsService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Perform linear regression analysis."""
    try:
        # Validate session and get data
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Perform linear regression
        result = await stats_service.linear_regression_analysis(
            df, request.target_column, request.feature_columns
        )
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in linear regression: {str(e)}")


@router.post("/regression/logistic")
async def logistic_regression(
    request: RegressionRequest,
    stats_service: StatisticsService = Depends(StatisticsService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Perform logistic regression analysis."""
    try:
        # Validate session and get data
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Perform logistic regression
        result = await stats_service.logistic_regression_analysis(
            df, request.target_column, request.feature_columns
        )
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in logistic regression: {str(e)}")


@router.post("/clustering")
async def clustering_analysis(
    request: ClusteringRequest,
    stats_service: StatisticsService = Depends(StatisticsService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Perform clustering analysis (K-means or hierarchical)."""
    try:
        # Validate session and get data
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Perform clustering
        result = await stats_service.clustering_analysis(
            df, request.columns, request.n_clusters, request.method
        )
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in clustering analysis: {str(e)}")


@router.post("/tests")
async def statistical_tests(
    request: StatisticalTestRequest,
    stats_service: StatisticsService = Depends(StatisticsService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Perform statistical significance tests."""
    try:
        # Validate session and get data
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Perform statistical test
        result = await stats_service.statistical_tests(
            df, request.test_type, **request.parameters
        )
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            "test_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in statistical test: {str(e)}")


@router.post("/visualization")
async def generate_visualization(
    request: VisualizationRequest,
    stats_service: StatisticsService = Depends(StatisticsService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Generate statistical visualizations."""
    try:
        # Validate session and get data
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Generate visualization
        image_base64 = await stats_service.generate_visualization(
            df, request.chart_type, **request.parameters
        )
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            "chart_type": request.chart_type,
            "image": f"data:image/png;base64,{image_base64}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")


@router.post("/analysis-summary")
async def get_analysis_summary(
    file_id: str,
    session_id: str,
    stats_service: StatisticsService = Depends(StatisticsService),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Get comprehensive analysis summary with recommendations."""
    try:
        # Validate session and get data
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get file data
        df = await data_service.get_file_data(file_id, session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Get analysis summary
        result = await stats_service.advanced_analysis_summary(df)
        
        return {
            "status": "success",
            "file_id": file_id,
            "session_id": session_id,
            "summary": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis summary: {str(e)}")


@router.get("/available-tests")
async def get_available_tests() -> Dict[str, Any]:
    """Get list of available statistical tests and their parameters."""
    return {
        "statistical_tests": [
            {
                "name": "correlation",
                "description": "Test correlation between two numeric variables",
                "parameters": ["column1", "column2", "method (pearson/spearman)"],
                "example": {
                    "test_type": "correlation",
                    "parameters": {
                        "column1": "age",
                        "column2": "income",
                        "method": "pearson"
                    }
                }
            },
            {
                "name": "t_test",
                "description": "Compare means between two groups",
                "parameters": ["group_column", "value_column"],
                "example": {
                    "test_type": "t_test",
                    "parameters": {
                        "group_column": "gender",
                        "value_column": "salary"
                    }
                }
            },
            {
                "name": "chi_square",
                "description": "Test independence between two categorical variables",
                "parameters": ["column1", "column2"],
                "example": {
                    "test_type": "chi_square",
                    "parameters": {
                        "column1": "education",
                        "column2": "employment_status"
                    }
                }
            }
        ],
        "regression_types": [
            {
                "name": "linear",
                "description": "Linear regression for continuous target variables",
                "use_case": "Predict continuous values"
            },
            {
                "name": "logistic",
                "description": "Logistic regression for categorical target variables",
                "use_case": "Classification problems"
            }
        ],
        "clustering_methods": [
            {
                "name": "kmeans",
                "description": "K-means clustering algorithm",
                "use_case": "Group similar data points into clusters"
            },
            {
                "name": "hierarchical",
                "description": "Hierarchical clustering algorithm",
                "use_case": "Create hierarchy of clusters"
            }
        ],
        "visualization_types": [
            {
                "name": "correlation_heatmap",
                "description": "Heatmap showing correlations between numeric variables"
            },
            {
                "name": "distribution",
                "description": "Distribution plot for a single variable",
                "parameters": ["column"]
            },
            {
                "name": "scatter",
                "description": "Scatter plot between two numeric variables",
                "parameters": ["x_column", "y_column"]
            }
        ]
    }