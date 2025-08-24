from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from app.services.performance_service import PerformanceMonitor
from app.services.data_processing_service import DataProcessingService
from app.services.session_service import SessionService
from app.schemas.performance import (
    DataOptimizationRequest,
    PerformanceReportRequest,
    SystemResourcesResponse,
    PerformanceReportResponse
)

router = APIRouter(prefix="/performance", tags=["performance"])


@router.post("/optimize-data")
async def optimize_dataframe(
    request: DataOptimizationRequest,
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor),
    data_service: DataProcessingService = Depends(DataProcessingService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Optimize DataFrame for better memory usage and performance"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get data
        df = await data_service.get_file_data(request.file_id, request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Optimize DataFrame
        optimized_df, optimizations = await perf_monitor.optimize_dataframe_operations(df)
        
        # Optionally cache optimized version
        if request.cache_optimized:
            cache_key = f"optimized_df_{request.file_id}_{request.session_id}"
            await perf_monitor.implement_caching_strategy(cache_key, optimized_df, expire_minutes=60)
        
        return {
            "status": "success",
            "file_id": request.file_id,
            "session_id": request.session_id,
            "original_shape": df.shape,
            "optimized_shape": optimized_df.shape,
            "optimizations_applied": optimizations,
            "cached": request.cache_optimized
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data optimization failed: {str(e)}")


@router.get("/system-resources")
async def get_system_resources(
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> SystemResourcesResponse:
    """Get current system resource usage and health status"""
    try:
        resources = await perf_monitor.monitor_system_resources()
        return SystemResourcesResponse(**resources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System monitoring failed: {str(e)}")


@router.get("/report")
async def get_performance_report(
    include_metrics: bool = True,
    include_recommendations: bool = True,
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> PerformanceReportResponse:
    """Generate comprehensive performance analysis report"""
    try:
        report = await perf_monitor.generate_performance_report()
        
        # Filter report based on parameters
        if not include_metrics:
            report.pop('performance_metrics', None)
        if not include_recommendations:
            report.pop('actionable_recommendations', None)
            report.pop('database_optimizations', None)
            report.pop('frontend_optimizations', None)
        
        return PerformanceReportResponse(**report)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance report generation failed: {str(e)}")


@router.get("/cache-stats")
async def get_cache_statistics(
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> Dict[str, Any]:
    """Get Redis cache usage statistics"""
    try:
        redis_client = perf_monitor.redis_client
        
        # Get Redis info
        redis_info = redis_client.info()
        
        # Get cache key statistics
        cache_keys = redis_client.keys(f"{perf_monitor.cache_prefix}*")
        metrics_keys = redis_client.keys(f"{perf_monitor.metrics_prefix}*")
        
        cache_stats = {
            "redis_connection": {
                "connected": redis_client.ping(),
                "memory_usage_mb": round(redis_info.get('used_memory', 0) / 1024 / 1024, 2),
                "total_connections": redis_info.get('connected_clients', 0),
                "total_keys": redis_info.get('db0', {}).get('keys', 0) if 'db0' in redis_info else 0
            },
            "cache_statistics": {
                "total_cached_items": len(cache_keys),
                "total_metrics": len(metrics_keys),
                "cache_keys_sample": [key.decode() for key in cache_keys[:10]],
                "metrics_keys_sample": [key.decode() for key in metrics_keys[:10]]
            },
            "performance_metrics": {
                "hit_rate": "N/A",  # Would need to implement hit/miss tracking
                "average_key_size": "N/A",  # Would need to calculate
                "expiry_info": "Keys expire based on TTL settings"
            }
        }
        
        return {
            "status": "success",
            "timestamp": redis_info.get('server_time_in_usec', 0),
            **cache_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache statistics failed: {str(e)}")


@router.post("/clear-cache")
async def clear_performance_cache(
    cache_type: Optional[str] = None,
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> Dict[str, Any]:
    """Clear performance-related cache entries"""
    try:
        redis_client = perf_monitor.redis_client
        cleared_count = 0
        
        if cache_type == "metrics" or cache_type is None:
            # Clear performance metrics
            metrics_keys = redis_client.keys(f"{perf_monitor.metrics_prefix}*")
            if metrics_keys:
                cleared_count += redis_client.delete(*metrics_keys)
        
        if cache_type == "data" or cache_type is None:
            # Clear cached data
            cache_keys = redis_client.keys(f"{perf_monitor.cache_prefix}*")
            if cache_keys:
                cleared_count += redis_client.delete(*cache_keys)
        
        return {
            "status": "success",
            "cache_type": cache_type or "all",
            "cleared_keys": cleared_count,
            "message": f"Cleared {cleared_count} cache entries"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clearing failed: {str(e)}")


@router.get("/database-optimization")
async def get_database_optimization_recommendations(
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> Dict[str, Any]:
    """Get database performance optimization recommendations"""
    try:
        optimizations = await perf_monitor.optimize_database_queries()
        
        return {
            "status": "success",
            "timestamp": perf_monitor.redis_client.time()[0],
            **optimizations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database optimization analysis failed: {str(e)}")


@router.get("/frontend-optimization")
async def get_frontend_optimization_recommendations(
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> Dict[str, Any]:
    """Get frontend performance optimization recommendations"""
    try:
        optimizations = await perf_monitor.optimize_frontend_performance()
        
        return {
            "status": "success",
            **optimizations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frontend optimization analysis failed: {str(e)}")


@router.get("/metrics/recent")
async def get_recent_performance_metrics(
    hours: int = 24,
    function_filter: Optional[str] = None,
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> Dict[str, Any]:
    """Get recent performance metrics with optional filtering"""
    try:
        metrics = await perf_monitor._get_recent_metrics(hours)
        
        # Filter by function name if specified
        if function_filter:
            metrics = [m for m in metrics if function_filter.lower() in m.get('function', '').lower()]
        
        # Calculate statistics
        if metrics:
            execution_times = [m.get('execution_time', 0) for m in metrics if m.get('success')]
            memory_usage = [m.get('memory_used_mb', 0) for m in metrics if m.get('success')]
            
            statistics = {
                "total_metrics": len(metrics),
                "successful_executions": len([m for m in metrics if m.get('success')]),
                "failed_executions": len([m for m in metrics if not m.get('success')]),
                "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
                "max_execution_time": max(execution_times) if execution_times else 0,
                "average_memory_usage": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                "unique_functions": len(set(m.get('function', '') for m in metrics))
            }
        else:
            statistics = {
                "total_metrics": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0,
                "max_execution_time": 0,
                "average_memory_usage": 0,
                "unique_functions": 0
            }
        
        return {
            "status": "success",
            "time_range_hours": hours,
            "function_filter": function_filter,
            "statistics": statistics,
            "metrics": metrics[:50]  # Limit to 50 most recent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


@router.get("/health-check")
async def performance_health_check(
    perf_monitor: PerformanceMonitor = Depends(PerformanceMonitor)
) -> Dict[str, Any]:
    """Quick performance health check endpoint"""
    try:
        # Get basic system resources
        resources = await perf_monitor.monitor_system_resources()
        system_health = resources.get('system_health', 'unknown')
        
        # Check Redis connectivity
        redis_healthy = perf_monitor.redis_client.ping()
        
        # Basic performance indicators
        cpu_usage = resources.get('cpu', {}).get('usage_percent', 0)
        memory_usage = resources.get('memory', {}).get('percentage', 0)
        
        health_status = "healthy"
        if system_health == "critical" or not redis_healthy:
            health_status = "critical"
        elif system_health == "warning" or cpu_usage > 80 or memory_usage > 80:
            health_status = "warning"
        
        return {
            "status": health_status,
            "timestamp": resources.get('timestamp'),
            "system_health": system_health,
            "redis_connected": redis_healthy,
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
            "recommendations": [
                "System running normally" if health_status == "healthy" else
                "Consider scaling resources" if health_status == "warning" else
                "Immediate attention required"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": None,
            "error": str(e),
            "recommendations": ["Check system connectivity and restart services"]
        }