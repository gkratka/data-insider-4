import uuid
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import redis
from celery.result import AsyncResult
from app.core.celery_app import celery_app
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "PENDING"
    STARTED = "STARTED"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"

class JobType(Enum):
    """Types of background jobs"""
    DATA_PROCESSING = "data_processing"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    ADVANCED_QUERY = "advanced_query"
    DATA_EXPORT = "data_export"
    CLEANUP = "cleanup"

class JobService:
    """Service for managing background jobs and their status"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.job_prefix = "job:"
        self.user_jobs_prefix = "user_jobs:"
        self.session_jobs_prefix = "session_jobs:"
        
    def generate_job_id(self) -> str:
        """Generate unique job ID"""
        return str(uuid.uuid4())
    
    async def submit_data_processing_job(
        self,
        file_id: str,
        session_id: str,
        operation_type: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Submit a data processing job to the background queue"""
        try:
            job_id = self.generate_job_id()
            
            # Submit task to Celery
            task = celery_app.send_task(
                'process_large_dataset',
                args=[file_id, session_id, operation_type],
                kwargs=kwargs,
                task_id=job_id
            )
            
            # Store job metadata
            job_info = {
                'job_id': job_id,
                'job_type': JobType.DATA_PROCESSING.value,
                'status': JobStatus.PENDING.value,
                'file_id': file_id,
                'session_id': session_id,
                'user_id': user_id,
                'operation_type': operation_type,
                'parameters': kwargs,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            await self._store_job_info(job_id, job_info)
            await self._add_to_user_jobs(user_id, job_id)
            await self._add_to_session_jobs(session_id, job_id)
            
            return {
                'job_id': job_id,
                'status': JobStatus.PENDING.value,
                'message': 'Data processing job submitted successfully',
                'estimated_completion': self._estimate_completion_time('data_processing')
            }
            
        except Exception as e:
            logger.error(f"Failed to submit data processing job: {str(e)}")
            raise Exception(f"Job submission failed: {str(e)}")
    
    async def submit_statistical_analysis_job(
        self,
        file_id: str,
        session_id: str,
        analysis_type: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Submit a statistical analysis job to the background queue"""
        try:
            job_id = self.generate_job_id()
            
            task = celery_app.send_task(
                'run_statistical_analysis',
                args=[file_id, session_id, analysis_type],
                kwargs=kwargs,
                task_id=job_id
            )
            
            job_info = {
                'job_id': job_id,
                'job_type': JobType.STATISTICAL_ANALYSIS.value,
                'status': JobStatus.PENDING.value,
                'file_id': file_id,
                'session_id': session_id,
                'user_id': user_id,
                'analysis_type': analysis_type,
                'parameters': kwargs,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            await self._store_job_info(job_id, job_info)
            await self._add_to_user_jobs(user_id, job_id)
            await self._add_to_session_jobs(session_id, job_id)
            
            return {
                'job_id': job_id,
                'status': JobStatus.PENDING.value,
                'message': 'Statistical analysis job submitted successfully',
                'estimated_completion': self._estimate_completion_time('statistical_analysis')
            }
            
        except Exception as e:
            logger.error(f"Failed to submit statistical analysis job: {str(e)}")
            raise Exception(f"Job submission failed: {str(e)}")
    
    async def submit_advanced_query_job(
        self,
        query: str,
        query_type: str,
        session_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Submit an advanced query job to the background queue"""
        try:
            job_id = self.generate_job_id()
            
            task = celery_app.send_task(
                'run_advanced_query',
                args=[query, query_type, session_id],
                kwargs=kwargs,
                task_id=job_id
            )
            
            job_info = {
                'job_id': job_id,
                'job_type': JobType.ADVANCED_QUERY.value,
                'status': JobStatus.PENDING.value,
                'query': query,
                'query_type': query_type,
                'session_id': session_id,
                'user_id': user_id,
                'parameters': kwargs,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            await self._store_job_info(job_id, job_info)
            await self._add_to_user_jobs(user_id, job_id)
            await self._add_to_session_jobs(session_id, job_id)
            
            return {
                'job_id': job_id,
                'status': JobStatus.PENDING.value,
                'message': 'Advanced query job submitted successfully',
                'estimated_completion': self._estimate_completion_time('advanced_query')
            }
            
        except Exception as e:
            logger.error(f"Failed to submit advanced query job: {str(e)}")
            raise Exception(f"Job submission failed: {str(e)}")
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the current status of a job"""
        try:
            # Get job info from Redis
            job_info = await self._get_job_info(job_id)
            if not job_info:
                return {'error': 'Job not found'}
            
            # Get task result from Celery
            result = AsyncResult(job_id, app=celery_app)
            
            # Update status from Celery result
            celery_status = result.status
            job_info['status'] = celery_status
            
            # Get additional info based on status
            if celery_status == 'PROGRESS':
                job_info['progress'] = result.info
            elif celery_status == 'SUCCESS':
                job_info['result'] = result.result
            elif celery_status == 'FAILURE':
                job_info['error'] = str(result.info)
            
            # Update timestamp
            job_info['updated_at'] = datetime.utcnow().isoformat()
            
            # Store updated info
            await self._store_job_info(job_id, job_info)
            
            return job_info
            
        except Exception as e:
            logger.error(f"Failed to get job status: {str(e)}")
            return {'error': f'Failed to get job status: {str(e)}'}
    
    async def cancel_job(self, job_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Cancel a running job"""
        try:
            # Check job ownership if user_id provided
            job_info = await self._get_job_info(job_id)
            if not job_info:
                return {'error': 'Job not found'}
            
            if user_id and job_info.get('user_id') != user_id:
                return {'error': 'Unauthorized to cancel this job'}
            
            # Revoke the Celery task
            celery_app.control.revoke(job_id, terminate=True)
            
            # Update job status
            job_info['status'] = JobStatus.REVOKED.value
            job_info['updated_at'] = datetime.utcnow().isoformat()
            job_info['cancelled_at'] = datetime.utcnow().isoformat()
            
            await self._store_job_info(job_id, job_info)
            
            return {
                'job_id': job_id,
                'status': JobStatus.REVOKED.value,
                'message': 'Job cancelled successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel job: {str(e)}")
            return {'error': f'Failed to cancel job: {str(e)}'}
    
    async def get_user_jobs(
        self,
        user_id: str,
        limit: int = 50,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all jobs for a specific user"""
        try:
            job_ids = self.redis_client.lrange(f"{self.user_jobs_prefix}{user_id}", 0, limit - 1)
            jobs = []
            
            for job_id in job_ids:
                job_info = await self._get_job_info(job_id.decode())
                if job_info:
                    # Filter by status if specified
                    if not status_filter or job_info.get('status') == status_filter:
                        jobs.append(job_info)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get user jobs: {str(e)}")
            return []
    
    async def get_session_jobs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all jobs for a specific session"""
        try:
            job_ids = self.redis_client.lrange(f"{self.session_jobs_prefix}{session_id}", 0, -1)
            jobs = []
            
            for job_id in job_ids:
                job_info = await self._get_job_info(job_id.decode())
                if job_info:
                    jobs.append(job_info)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get session jobs: {str(e)}")
            return []
    
    async def cleanup_old_jobs(self, days_old: int = 7) -> int:
        """Clean up job records older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cleaned_count = 0
            
            # Get all job keys
            job_keys = self.redis_client.keys(f"{self.job_prefix}*")
            
            for job_key in job_keys:
                job_data = self.redis_client.get(job_key)
                if job_data:
                    job_info = json.loads(job_data.decode())
                    created_at = datetime.fromisoformat(job_info.get('created_at', ''))
                    
                    if created_at < cutoff_date:
                        # Delete job record
                        self.redis_client.delete(job_key)
                        cleaned_count += 1
                        
                        # Remove from user and session job lists
                        job_id = job_key.decode().replace(self.job_prefix, '')
                        user_id = job_info.get('user_id')
                        session_id = job_info.get('session_id')
                        
                        if user_id:
                            self.redis_client.lrem(f"{self.user_jobs_prefix}{user_id}", 0, job_id)
                        if session_id:
                            self.redis_client.lrem(f"{self.session_jobs_prefix}{session_id}", 0, job_id)
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {str(e)}")
            return 0
    
    # Private helper methods
    async def _store_job_info(self, job_id: str, job_info: Dict[str, Any]) -> None:
        """Store job information in Redis"""
        self.redis_client.set(
            f"{self.job_prefix}{job_id}",
            json.dumps(job_info),
            ex=604800  # Expire after 7 days
        )
    
    async def _get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information from Redis"""
        job_data = self.redis_client.get(f"{self.job_prefix}{job_id}")
        if job_data:
            return json.loads(job_data.decode())
        return None
    
    async def _add_to_user_jobs(self, user_id: Optional[str], job_id: str) -> None:
        """Add job to user's job list"""
        if user_id:
            self.redis_client.lpush(f"{self.user_jobs_prefix}{user_id}", job_id)
            self.redis_client.ltrim(f"{self.user_jobs_prefix}{user_id}", 0, 99)  # Keep last 100 jobs
    
    async def _add_to_session_jobs(self, session_id: str, job_id: str) -> None:
        """Add job to session's job list"""
        self.redis_client.lpush(f"{self.session_jobs_prefix}{session_id}", job_id)
        self.redis_client.ltrim(f"{self.session_jobs_prefix}{session_id}", 0, 49)  # Keep last 50 jobs
    
    def _estimate_completion_time(self, job_type: str) -> str:
        """Estimate job completion time based on type"""
        estimates = {
            'data_processing': '2-5 minutes',
            'statistical_analysis': '3-10 minutes',
            'advanced_query': '1-3 minutes',
            'data_export': '1-2 minutes',
            'cleanup': '< 1 minute'
        }
        return estimates.get(job_type, '2-5 minutes')