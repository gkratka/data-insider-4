from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime

class JobSubmissionRequest(BaseModel):
    """Request schema for job submission"""
    session_id: str = Field(..., description="Session identifier")
    file_id: str = Field(..., description="File identifier")
    operation_type: str = Field(..., description="Type of operation to perform")
    user_id: Optional[str] = Field(None, description="User identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation-specific parameters")

class JobStatusResponse(BaseModel):
    """Response schema for job status"""
    job_id: str
    job_type: str
    status: str
    file_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: str
    updated_at: str
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    estimated_completion: Optional[str] = None

class JobListResponse(BaseModel):
    """Response schema for job listings"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    total_jobs: int
    jobs: List[JobStatusResponse]
    filters: Optional[Dict[str, Any]] = None

class JobCancellationResponse(BaseModel):
    """Response schema for job cancellation"""
    job_id: str
    status: str
    message: str

class JobProgressUpdate(BaseModel):
    """Schema for job progress updates"""
    current: int = Field(ge=0, le=100, description="Current progress percentage")
    total: int = Field(100, description="Total progress (usually 100)")
    status: str = Field(..., description="Current status message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional progress details")

class JobResult(BaseModel):
    """Schema for job results"""
    status: str
    operation_type: Optional[str] = None
    analysis_type: Optional[str] = None
    query_type: Optional[str] = None
    result_data: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    rows_processed: Optional[int] = None

class BackgroundJobConfig(BaseModel):
    """Configuration for background job execution"""
    queue_name: Optional[str] = Field("default", description="Celery queue name")
    priority: Optional[int] = Field(5, ge=1, le=10, description="Job priority (1=lowest, 10=highest)")
    max_retries: Optional[int] = Field(3, ge=0, le=10, description="Maximum retry attempts")
    retry_delay: Optional[int] = Field(60, ge=1, description="Retry delay in seconds")
    soft_time_limit: Optional[int] = Field(300, description="Soft time limit in seconds")
    hard_time_limit: Optional[int] = Field(600, description="Hard time limit in seconds")
    
class JobNotification(BaseModel):
    """Schema for job completion notifications"""
    job_id: str
    job_type: str
    status: Literal["SUCCESS", "FAILURE"]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    completion_time: datetime
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    
class JobMetrics(BaseModel):
    """Schema for job execution metrics"""
    job_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_duration: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_time_seconds: Optional[float] = None
    rows_processed: Optional[int] = None
    data_size_mb: Optional[float] = None
    queue_wait_time: Optional[float] = None

class JobStatistics(BaseModel):
    """Schema for job statistics and analytics"""
    total_jobs: int
    jobs_by_status: Dict[str, int]
    jobs_by_type: Dict[str, int]
    average_execution_time: Optional[float] = None
    success_rate: Optional[float] = None
    most_common_operations: List[Dict[str, Any]]
    peak_usage_hours: List[int]
    failed_job_reasons: Dict[str, int]

class JobQueueStatus(BaseModel):
    """Schema for job queue status"""
    queue_name: str
    pending_jobs: int
    running_jobs: int
    failed_jobs: int
    completed_jobs: int
    average_wait_time: Optional[float] = None
    estimated_processing_time: Optional[str] = None