import time
import psutil
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from functools import wraps
import redis
from app.core.config import get_settings
from app.services.data_processing_service import DataProcessingService

logger = logging.getLogger(__name__)
settings = get_settings()

class PerformanceMonitor:
    """Service for monitoring and optimizing application performance"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.metrics_prefix = "perf_metrics:"
        self.cache_prefix = "cache:"
        
    def measure_execution_time(self, func_name: str = None):
        """Decorator to measure function execution time"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                try:
                    result = await func(*args, **kwargs)
                    
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    execution_time = end_time - start_time
                    memory_used = end_memory - start_memory
                    
                    # Store metrics
                    await self._store_performance_metric(
                        func_name or func.__name__,
                        execution_time,
                        memory_used,
                        True
                    )
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    await self._store_performance_metric(
                        func_name or func.__name__,
                        execution_time,
                        0,
                        False,
                        str(e)
                    )
                    raise
                    
            return wrapper
        return decorator
    
    async def optimize_dataframe_operations(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Optimize DataFrame for better performance"""
        optimizations_applied = {}
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        
        # Create copy to avoid modifying original
        optimized_df = df.copy()
        
        # 1. Optimize data types
        type_optimizations = {}
        
        for col in optimized_df.columns:
            original_dtype = optimized_df[col].dtype
            
            if optimized_df[col].dtype == 'object':
                # Try to convert to categorical if low cardinality
                unique_ratio = optimized_df[col].nunique() / len(optimized_df)
                if unique_ratio < 0.1:  # Less than 10% unique values
                    optimized_df[col] = optimized_df[col].astype('category')
                    type_optimizations[col] = {'from': str(original_dtype), 'to': 'category'}
                    
            elif optimized_df[col].dtype in ['int64', 'int32']:
                # Downcast integers
                col_min, col_max = optimized_df[col].min(), optimized_df[col].max()
                
                if col_min >= 0:  # Unsigned integers
                    if col_max < 256:
                        optimized_df[col] = optimized_df[col].astype('uint8')
                        type_optimizations[col] = {'from': str(original_dtype), 'to': 'uint8'}
                    elif col_max < 65536:
                        optimized_df[col] = optimized_df[col].astype('uint16')
                        type_optimizations[col] = {'from': str(original_dtype), 'to': 'uint16'}
                    elif col_max < 4294967296:
                        optimized_df[col] = optimized_df[col].astype('uint32')
                        type_optimizations[col] = {'from': str(original_dtype), 'to': 'uint32'}
                else:  # Signed integers
                    if col_min >= -128 and col_max < 128:
                        optimized_df[col] = optimized_df[col].astype('int8')
                        type_optimizations[col] = {'from': str(original_dtype), 'to': 'int8'}
                    elif col_min >= -32768 and col_max < 32768:
                        optimized_df[col] = optimized_df[col].astype('int16')
                        type_optimizations[col] = {'from': str(original_dtype), 'to': 'int16'}
                    elif col_min >= -2147483648 and col_max < 2147483648:
                        optimized_df[col] = optimized_df[col].astype('int32')
                        type_optimizations[col] = {'from': str(original_dtype), 'to': 'int32'}
                        
            elif optimized_df[col].dtype == 'float64':
                # Downcast floats
                optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
                new_dtype = optimized_df[col].dtype
                if new_dtype != original_dtype:
                    type_optimizations[col] = {'from': str(original_dtype), 'to': str(new_dtype)}
        
        optimizations_applied['data_type_optimizations'] = type_optimizations
        
        # 2. Remove duplicate rows
        original_rows = len(optimized_df)
        optimized_df = optimized_df.drop_duplicates()
        duplicates_removed = original_rows - len(optimized_df)
        optimizations_applied['duplicates_removed'] = duplicates_removed
        
        # 3. Handle missing values efficiently
        missing_before = optimized_df.isnull().sum().sum()
        # For now, just record missing values; specific handling would depend on use case
        optimizations_applied['missing_values'] = missing_before
        
        # Calculate memory savings
        optimized_memory = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        memory_saved = original_memory - optimized_memory
        memory_reduction_pct = (memory_saved / original_memory) * 100 if original_memory > 0 else 0
        
        optimizations_applied['memory_optimization'] = {
            'original_memory_mb': round(original_memory, 2),
            'optimized_memory_mb': round(optimized_memory, 2),
            'memory_saved_mb': round(memory_saved, 2),
            'reduction_percentage': round(memory_reduction_pct, 2)
        }
        
        return optimized_df, optimizations_applied
    
    async def implement_caching_strategy(self, cache_key: str, data: Any, expire_minutes: int = 30) -> bool:
        """Implement intelligent caching for frequently accessed data"""
        try:
            # Serialize data based on type
            if isinstance(data, pd.DataFrame):
                # Cache DataFrame as parquet-like structure
                cached_data = {
                    'type': 'dataframe',
                    'data': data.to_dict('records'),
                    'columns': data.columns.tolist(),
                    'dtypes': data.dtypes.astype(str).to_dict(),
                    'shape': data.shape
                }
            else:
                cached_data = {
                    'type': 'generic',
                    'data': data
                }
            
            # Store in Redis with expiration
            import json
            self.redis_client.setex(
                f"{self.cache_prefix}{cache_key}",
                expire_minutes * 60,
                json.dumps(cached_data, default=str)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Caching failed for key {cache_key}: {str(e)}")
            return False
    
    async def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached data"""
        try:
            cached_str = self.redis_client.get(f"{self.cache_prefix}{cache_key}")
            if not cached_str:
                return None
            
            import json
            cached_data = json.loads(cached_str.decode())
            
            if cached_data.get('type') == 'dataframe':
                # Reconstruct DataFrame
                df = pd.DataFrame(cached_data['data'])
                # Restore data types
                for col, dtype in cached_data['dtypes'].items():
                    if col in df.columns:
                        try:
                            df[col] = df[col].astype(dtype)
                        except:
                            pass
                return df
            else:
                return cached_data.get('data')
                
        except Exception as e:
            logger.error(f"Cache retrieval failed for key {cache_key}: {str(e)}")
            return None
    
    async def optimize_database_queries(self) -> Dict[str, Any]:
        """Analyze and optimize database query performance"""
        optimizations = {
            'recommendations': [],
            'current_performance': {},
            'optimization_strategies': []
        }
        
        # Database connection analysis
        try:
            # This would connect to actual database in production
            optimizations['recommendations'].extend([
                "Add database indexes on frequently queried columns",
                "Implement connection pooling for better resource utilization",
                "Use database-specific optimizations (EXPLAIN ANALYZE for PostgreSQL)",
                "Consider read replicas for read-heavy workloads",
                "Implement query result caching at database level"
            ])
            
            optimizations['optimization_strategies'].extend([
                {
                    'strategy': 'Index Optimization',
                    'description': 'Create composite indexes on commonly queried column combinations',
                    'expected_improvement': '50-80% query time reduction'
                },
                {
                    'strategy': 'Connection Pooling',
                    'description': 'Implement connection pooling to reduce connection overhead',
                    'expected_improvement': '20-40% throughput increase'
                },
                {
                    'strategy': 'Query Optimization',
                    'description': 'Optimize slow queries using database-specific techniques',
                    'expected_improvement': '30-70% query time reduction'
                }
            ])
            
        except Exception as e:
            logger.error(f"Database optimization analysis failed: {str(e)}")
        
        return optimizations
    
    async def optimize_frontend_performance(self) -> Dict[str, Any]:
        """Provide frontend performance optimization recommendations"""
        return {
            'bundle_optimization': {
                'recommendations': [
                    "Implement code splitting for lazy loading of components",
                    "Use tree shaking to eliminate unused code",
                    "Optimize images with WebP format and lazy loading",
                    "Implement service worker for caching strategies",
                    "Minimize and compress CSS/JavaScript bundles"
                ],
                'tools': ['webpack-bundle-analyzer', 'lighthouse', 'web-vitals']
            },
            'react_optimizations': {
                'recommendations': [
                    "Use React.memo for expensive components",
                    "Implement useMemo and useCallback for expensive calculations",
                    "Optimize list rendering with React.Window or virtualization",
                    "Implement proper key props for list items",
                    "Use React DevTools Profiler to identify performance bottlenecks"
                ]
            },
            'data_fetching_optimizations': {
                'recommendations': [
                    "Implement proper loading states and skeleton screens",
                    "Use React Query for intelligent caching and background updates",
                    "Implement pagination for large datasets",
                    "Use WebSocket for real-time updates instead of polling",
                    "Implement request deduplication and batching"
                ]
            },
            'metrics_to_monitor': [
                'First Contentful Paint (FCP)',
                'Largest Contentful Paint (LCP)',
                'First Input Delay (FID)',
                'Cumulative Layout Shift (CLS)',
                'Time to Interactive (TTI)'
            ]
        }
    
    async def monitor_system_resources(self) -> Dict[str, Any]:
        """Monitor current system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = {
                'total_gb': round(memory.total / 1024 / 1024 / 1024, 2),
                'available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
                'used_gb': round(memory.used / 1024 / 1024 / 1024, 2),
                'percentage': memory.percent
            }
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = {
                'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                'percentage': round((disk.used / disk.total) * 100, 2)
            }
            
            # Process-specific information
            process = psutil.Process()
            process_info = {
                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
                'cpu_percent': process.cpu_percent(),
                'threads': process.num_threads(),
                'connections': len(process.connections()),
                'open_files': len(process.open_files())
            }
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'core_count': cpu_count
                },
                'memory': memory_usage,
                'disk': disk_usage,
                'process': process_info,
                'system_health': self._assess_system_health(cpu_percent, memory.percent, disk_usage['percentage'])
            }
            
        except Exception as e:
            logger.error(f"System monitoring failed: {str(e)}")
            return {'error': str(e)}
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""
        try:
            # Get recent metrics
            recent_metrics = await self._get_recent_metrics()
            
            # System resources
            system_resources = await self.monitor_system_resources()
            
            # Database optimization recommendations
            db_optimizations = await self.optimize_database_queries()
            
            # Frontend optimization recommendations
            frontend_optimizations = await self.optimize_frontend_performance()
            
            report = {
                'report_timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'overall_health': system_resources.get('system_health', 'unknown'),
                    'total_metrics_analyzed': len(recent_metrics),
                    'recommendations_count': (
                        len(db_optimizations.get('recommendations', [])) +
                        len(frontend_optimizations.get('bundle_optimization', {}).get('recommendations', []))
                    )
                },
                'system_resources': system_resources,
                'performance_metrics': recent_metrics,
                'database_optimizations': db_optimizations,
                'frontend_optimizations': frontend_optimizations,
                'actionable_recommendations': self._generate_actionable_recommendations(
                    system_resources, recent_metrics
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Performance report generation failed: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    async def _store_performance_metric(
        self, 
        function_name: str, 
        execution_time: float, 
        memory_used: float, 
        success: bool,
        error_message: str = None
    ):
        """Store performance metric in Redis"""
        try:
            metric = {
                'timestamp': datetime.utcnow().isoformat(),
                'function': function_name,
                'execution_time': execution_time,
                'memory_used_mb': memory_used,
                'success': success,
                'error': error_message
            }
            
            import json
            key = f"{self.metrics_prefix}{function_name}:{int(time.time())}"
            self.redis_client.setex(key, 3600, json.dumps(metric))  # Store for 1 hour
            
        except Exception as e:
            logger.error(f"Failed to store performance metric: {str(e)}")
    
    async def _get_recent_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance metrics from the last N hours"""
        try:
            pattern = f"{self.metrics_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            metrics = []
            for key in keys:
                try:
                    data = self.redis_client.get(key)
                    if data:
                        import json
                        metric = json.loads(data.decode())
                        # Filter by timestamp
                        metric_time = datetime.fromisoformat(metric['timestamp'])
                        if metric_time > datetime.utcnow() - timedelta(hours=hours):
                            metrics.append(metric)
                except:
                    continue
            
            return sorted(metrics, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to retrieve recent metrics: {str(e)}")
            return []
    
    def _assess_system_health(self, cpu_percent: float, memory_percent: float, disk_percent: float) -> str:
        """Assess overall system health based on resource usage"""
        if cpu_percent > 90 or memory_percent > 95 or disk_percent > 95:
            return 'critical'
        elif cpu_percent > 70 or memory_percent > 80 or disk_percent > 80:
            return 'warning'
        elif cpu_percent > 50 or memory_percent > 60 or disk_percent > 60:
            return 'moderate'
        else:
            return 'good'
    
    def _generate_actionable_recommendations(self, system_resources: Dict, metrics: List[Dict]) -> List[Dict[str, str]]:
        """Generate specific actionable recommendations based on current state"""
        recommendations = []
        
        # CPU-based recommendations
        cpu_usage = system_resources.get('cpu', {}).get('usage_percent', 0)
        if cpu_usage > 80:
            recommendations.append({
                'category': 'CPU',
                'priority': 'high',
                'recommendation': 'Consider scaling horizontally or optimizing CPU-intensive operations'
            })
        
        # Memory-based recommendations
        memory_usage = system_resources.get('memory', {}).get('percentage', 0)
        if memory_usage > 85:
            recommendations.append({
                'category': 'Memory',
                'priority': 'high', 
                'recommendation': 'Implement data pagination or increase available memory'
            })
        
        # Performance metrics recommendations
        slow_functions = [m for m in metrics if m.get('execution_time', 0) > 5.0]
        if slow_functions:
            recommendations.append({
                'category': 'Performance',
                'priority': 'medium',
                'recommendation': f'Optimize slow functions: {", ".join(set(f["function"] for f in slow_functions[:5]))}'
            })
        
        return recommendations