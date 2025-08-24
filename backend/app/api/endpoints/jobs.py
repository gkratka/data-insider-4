from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from app.services.job_service import JobService, JobStatus, JobType
from app.services.session_service import SessionService
from app.schemas.jobs import (
    JobSubmissionRequest,
    JobStatusResponse,
    JobListResponse,
    JobCancellationResponse
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/data-processing")
async def submit_data_processing_job(
    request: JobSubmissionRequest,
    job_service: JobService = Depends(JobService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Submit a data processing job for background execution"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Submit job
        result = await job_service.submit_data_processing_job(
            file_id=request.file_id,
            session_id=request.session_id,
            operation_type=request.operation_type,
            user_id=request.user_id,
            **request.parameters
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")


@router.post("/statistical-analysis")
async def submit_statistical_analysis_job(
    request: JobSubmissionRequest,
    job_service: JobService = Depends(JobService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Submit a statistical analysis job for background execution"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Submit job
        result = await job_service.submit_statistical_analysis_job(
            file_id=request.file_id,
            session_id=request.session_id,
            analysis_type=request.operation_type,
            user_id=request.user_id,
            **request.parameters
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit analysis job: {str(e)}")


@router.post("/advanced-query")
async def submit_advanced_query_job(
    query: str,
    query_type: str,
    session_id: str,
    user_id: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    job_service: JobService = Depends(JobService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Submit an advanced query job for background execution"""
    try:
        # Validate session
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Submit job
        result = await job_service.submit_advanced_query_job(
            query=query,
            query_type=query_type,
            session_id=session_id,
            user_id=user_id,
            **(parameters or {})
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit query job: {str(e)}")


@router.get("/{job_id}/status")
async def get_job_status(
    job_id: str,
    job_service: JobService = Depends(JobService)
) -> Dict[str, Any]:
    """Get the current status and progress of a job"""
    try:
        status = await job_service.get_job_status(job_id)
        
        if 'error' in status:
            raise HTTPException(status_code=404, detail=status['error'])
        
        return {
            "job_id": job_id,
            **status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    user_id: Optional[str] = None,
    job_service: JobService = Depends(JobService)
) -> Dict[str, Any]:
    """Cancel a running or pending job"""
    try:
        result = await job_service.cancel_job(job_id, user_id)
        
        if 'error' in result:
            if 'Unauthorized' in result['error']:
                raise HTTPException(status_code=403, detail=result['error'])
            else:
                raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_jobs(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    job_service: JobService = Depends(JobService)
) -> Dict[str, Any]:
    """Get all jobs for a specific user"""
    try:
        jobs = await job_service.get_user_jobs(user_id, limit, status_filter)
        
        return {
            "user_id": user_id,
            "total_jobs": len(jobs),
            "jobs": jobs,
            "filters": {
                "limit": limit,
                "status_filter": status_filter
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user jobs: {str(e)}")


@router.get("/session/{session_id}")
async def get_session_jobs(
    session_id: str,
    job_service: JobService = Depends(JobService),
    session_service: SessionService = Depends(SessionService)
) -> Dict[str, Any]:
    """Get all jobs for a specific session"""
    try:
        # Validate session
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        jobs = await job_service.get_session_jobs(session_id)
        
        return {
            "session_id": session_id,
            "total_jobs": len(jobs),
            "jobs": jobs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session jobs: {str(e)}")


@router.get("/status/summary")
async def get_job_status_summary(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    job_service: JobService = Depends(JobService)
) -> Dict[str, Any]:
    """Get a summary of job statuses"""
    try:
        if user_id:
            jobs = await job_service.get_user_jobs(user_id, limit=100)
        elif session_id:
            jobs = await job_service.get_session_jobs(session_id)
        else:
            raise HTTPException(status_code=400, detail="Either user_id or session_id must be provided")
        
        # Calculate status summary
        status_counts = {}
        job_type_counts = {}
        
        for job in jobs:
            status = job.get('status', 'UNKNOWN')
            job_type = job.get('job_type', 'unknown')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            job_type_counts[job_type] = job_type_counts.get(job_type, 0) + 1
        
        # Get running jobs
        running_jobs = [job for job in jobs if job.get('status') in ['PENDING', 'STARTED', 'PROGRESS']]
        
        return {
            "total_jobs": len(jobs),
            "status_summary": status_counts,
            "job_type_summary": job_type_counts,
            "running_jobs_count": len(running_jobs),
            "running_jobs": running_jobs[:5],  # Show first 5 running jobs
            "last_updated": jobs[0].get('updated_at') if jobs else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job summary: {str(e)}")


@router.delete("/cleanup")
async def cleanup_old_jobs(
    days_old: int = Query(7, ge=1, le=30),
    job_service: JobService = Depends(JobService)
) -> Dict[str, Any]:
    """Clean up old job records (admin operation)"""
    try:
        cleaned_count = await job_service.cleanup_old_jobs(days_old)
        
        return {
            "message": f"Cleaned up {cleaned_count} old jobs",
            "days_old": days_old,
            "cleaned_jobs": cleaned_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup jobs: {str(e)}")


@router.get("/available-operations")
async def get_available_operations() -> Dict[str, Any]:
    """Get list of available job operations and their parameters"""
    return {
        "data_processing_operations": [
            {
                "type": "filter",
                "description": "Filter dataset based on conditions",
                "parameters": ["conditions (dict)"],
                "example": {
                    "operation_type": "filter",
                    "parameters": {
                        "conditions": {"column1": {"operator": ">=", "value": 100}}
                    }
                }
            },
            {
                "type": "aggregate", 
                "description": "Aggregate data with grouping",
                "parameters": ["group_columns (list)", "agg_functions (dict)"],
                "example": {
                    "operation_type": "aggregate",
                    "parameters": {
                        "group_columns": ["category"],
                        "agg_functions": {"sales": ["sum", "mean"]}
                    }
                }
            },
            {
                "type": "sort",
                "description": "Sort dataset by columns",
                "parameters": ["columns (list)", "ascending (bool)"],
                "example": {
                    "operation_type": "sort", 
                    "parameters": {
                        "columns": ["date", "amount"],
                        "ascending": [True, False]
                    }
                }
            }
        ],
        "statistical_analysis_operations": [
            {
                "type": "descriptive",
                "description": "Calculate descriptive statistics",
                "parameters": ["columns (optional list)"]
            },
            {
                "type": "linear_regression",
                "description": "Perform linear regression analysis",
                "parameters": ["target_column (str)", "feature_columns (optional list)"]
            },
            {
                "type": "logistic_regression", 
                "description": "Perform logistic regression analysis",
                "parameters": ["target_column (str)", "feature_columns (optional list)"]
            },
            {
                "type": "clustering",
                "description": "Perform clustering analysis",
                "parameters": ["columns (optional list)", "n_clusters (int)", "method (str)"]
            },
            {
                "type": "statistical_test",
                "description": "Perform statistical significance tests",
                "parameters": ["test_type (str)", "parameters (dict)"]
            }
        ],
        "advanced_query_operations": [
            {
                "type": "multi_table_join",
                "description": "Join multiple tables",
                "parameters": ["file_ids (list)", "join_keys (optional dict)", "join_type (str)"]
            },
            {
                "type": "complex_aggregation",
                "description": "Complex aggregation operations",
                "parameters": ["file_id (str)", "group_columns (optional list)", "agg_functions (optional dict)"]
            },
            {
                "type": "time_series_analysis",
                "description": "Time series analysis operations", 
                "parameters": ["file_id (str)", "date_column (optional str)", "value_columns (optional list)", "operation (optional str)"]
            }
        ],
        "job_statuses": [status.value for status in JobStatus],
        "job_types": [job_type.value for job_type in JobType]
    }