import logging
from typing import Dict, Any, Optional, List
from celery import current_task
from app.core.celery_app import celery_app
from app.services.data_processing_service import DataProcessingService
from app.services.statistics_service import StatisticsService
from app.services.advanced_query_processor import AdvancedQueryProcessor
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="process_large_dataset")
def process_large_dataset(self, file_id: str, session_id: str, operation_type: str, **kwargs) -> Dict[str, Any]:
    """
    Process large datasets in the background to avoid blocking the API.
    
    Args:
        file_id: ID of the file to process
        session_id: Session identifier
        operation_type: Type of operation (filter, aggregate, analyze)
        **kwargs: Additional parameters for the operation
    """
    try:
        # Update task status
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Initializing...'}
        )
        
        data_service = DataProcessingService()
        
        # Load data with progress tracking
        current_task.update_state(
            state='PROGRESS', 
            meta={'current': 20, 'total': 100, 'status': 'Loading dataset...'}
        )
        
        df = await data_service.get_file_data(file_id, session_id)
        if df is None:
            raise Exception("Failed to load dataset")
        
        # Process based on operation type
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 40, 'total': 100, 'status': f'Executing {operation_type}...'}
        )
        
        result = None
        
        if operation_type == "filter":
            filter_conditions = kwargs.get("conditions", {})
            result = await data_service.filter_data(df, filter_conditions)
            
        elif operation_type == "aggregate":
            group_columns = kwargs.get("group_columns", [])
            agg_functions = kwargs.get("agg_functions", {})
            result = await data_service.aggregate_data(df, group_columns, agg_functions)
            
        elif operation_type == "sort":
            sort_columns = kwargs.get("columns", [])
            ascending = kwargs.get("ascending", True)
            result = await data_service.sort_data(df, sort_columns, ascending)
            
        else:
            raise ValueError(f"Unsupported operation type: {operation_type}")
        
        # Finalize result
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Finalizing results...'}
        )
        
        # Convert result to serializable format
        if hasattr(result, 'to_dict'):
            result_data = result.head(1000).to_dict('records')  # Limit to 1000 rows
            total_rows = len(result)
        else:
            result_data = {"result": str(result)}
            total_rows = 1
        
        return {
            'status': 'completed',
            'operation_type': operation_type,
            'result_data': result_data,
            'total_rows': total_rows,
            'file_id': file_id,
            'session_id': session_id,
            'metadata': {
                'processing_time': current_task.request.time_limit,
                'rows_processed': len(df) if df is not None else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e), 'status': 'Task failed'}
        )
        raise


@celery_app.task(bind=True, name="run_statistical_analysis")
def run_statistical_analysis(self, file_id: str, session_id: str, analysis_type: str, **kwargs) -> Dict[str, Any]:
    """
    Run statistical analysis on large datasets in the background.
    
    Args:
        file_id: ID of the file to analyze
        session_id: Session identifier  
        analysis_type: Type of analysis (descriptive, regression, clustering)
        **kwargs: Analysis-specific parameters
    """
    try:
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting statistical analysis...'}
        )
        
        stats_service = StatisticsService()
        data_service = DataProcessingService()
        
        # Load data
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 15, 'total': 100, 'status': 'Loading dataset...'}
        )
        
        df = await data_service.get_file_data(file_id, session_id)
        if df is None:
            raise Exception("Failed to load dataset")
        
        # Run analysis based on type
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': f'Running {analysis_type} analysis...'}
        )
        
        result = None
        
        if analysis_type == "descriptive":
            columns = kwargs.get("columns")
            result = await stats_service.descriptive_statistics(df, columns)
            
        elif analysis_type == "linear_regression":
            target_col = kwargs.get("target_column")
            feature_cols = kwargs.get("feature_columns")
            result = await stats_service.linear_regression_analysis(df, target_col, feature_cols)
            
        elif analysis_type == "logistic_regression":
            target_col = kwargs.get("target_column") 
            feature_cols = kwargs.get("feature_columns")
            result = await stats_service.logistic_regression_analysis(df, target_col, feature_cols)
            
        elif analysis_type == "clustering":
            columns = kwargs.get("columns")
            n_clusters = kwargs.get("n_clusters", 3)
            method = kwargs.get("method", "kmeans")
            result = await stats_service.clustering_analysis(df, columns, n_clusters, method)
            
        elif analysis_type == "statistical_test":
            test_type = kwargs.get("test_type")
            parameters = kwargs.get("parameters", {})
            result = await stats_service.statistical_tests(df, test_type, **parameters)
            
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing analysis...'}
        )
        
        return {
            'status': 'completed',
            'analysis_type': analysis_type,
            'result': result,
            'file_id': file_id,
            'session_id': session_id,
            'metadata': {
                'dataset_shape': df.shape,
                'analysis_parameters': kwargs
            }
        }
        
    except Exception as e:
        logger.error(f"Statistical analysis task failed: {str(e)}")
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e), 'status': 'Analysis failed'}
        )
        raise


@celery_app.task(bind=True, name="run_advanced_query")
def run_advanced_query(self, query: str, query_type: str, session_id: str, **kwargs) -> Dict[str, Any]:
    """
    Execute advanced queries (joins, complex aggregations, time series) in background.
    
    Args:
        query: Natural language query
        query_type: Type of advanced query (join, aggregation, time_series)
        session_id: Session identifier
        **kwargs: Query-specific parameters
    """
    try:
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Processing advanced query...'}
        )
        
        advanced_processor = AdvancedQueryProcessor()
        data_service = DataProcessingService()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': 'Loading required datasets...'}
        )
        
        result = None
        
        if query_type == "multi_table_join":
            file_ids = kwargs.get("file_ids", [])
            join_keys = kwargs.get("join_keys")
            join_type = kwargs.get("join_type", "inner")
            
            # Get file records (simplified - in real implementation would use proper DB session)
            file_records = []  # TODO: Implement proper file record retrieval
            
            result = await advanced_processor.process_multi_table_join(
                query, file_records, session_id, join_keys, join_type
            )
            
        elif query_type == "complex_aggregation":
            file_id = kwargs.get("file_id")
            group_columns = kwargs.get("group_columns")
            agg_functions = kwargs.get("agg_functions")
            
            df = await data_service.get_file_data(file_id, session_id)
            result = await advanced_processor.process_complex_aggregation(
                query, df, group_columns, agg_functions
            )
            
        elif query_type == "time_series_analysis":
            file_id = kwargs.get("file_id")
            date_column = kwargs.get("date_column")
            value_columns = kwargs.get("value_columns")
            operation = kwargs.get("operation")
            
            df = await data_service.get_file_data(file_id, session_id)
            result = await advanced_processor.process_time_series_analysis(
                query, df, date_column, value_columns, operation
            )
            
        else:
            raise ValueError(f"Unsupported query type: {query_type}")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing query results...'}
        )
        
        return {
            'status': 'completed',
            'query_type': query_type,
            'query': query,
            'result': result,
            'session_id': session_id,
            'parameters': kwargs
        }
        
    except Exception as e:
        logger.error(f"Advanced query task failed: {str(e)}")
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e), 'status': 'Query execution failed'}
        )
        raise


@celery_app.task(bind=True, name="cleanup_expired_sessions")
def cleanup_expired_sessions(self) -> Dict[str, Any]:
    """
    Background task to clean up expired sessions and temporary data.
    """
    try:
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting cleanup...'}
        )
        
        session_service = SessionService()
        
        # Clean up expired sessions
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Cleaning expired sessions...'}
        )
        
        cleanup_count = await session_service.cleanup_expired_sessions()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Cleanup completed...'}
        )
        
        return {
            'status': 'completed',
            'cleaned_sessions': cleanup_count,
            'cleanup_time': current_task.request.time_limit
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise