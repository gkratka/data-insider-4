from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.data_processing import (
    DataQuery, DataSummaryResponse, DataPreviewResponse, 
    DataOperationResponse, FilterCondition, AggregationRequest, SortColumn
)
from app.services.data_processing_service import data_processing_engine
from app.services.file_service import FileService
from app.auth.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()
file_service = FileService()


@router.get("/{file_id}/summary", response_model=DataSummaryResponse)
async def get_data_summary(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get comprehensive summary of uploaded data file
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = await data_processing_engine.load_file_data(file_record)
        summary = data_processing_engine.get_data_summary(df)
        
        return DataSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/{file_id}/preview", response_model=DataPreviewResponse)
async def get_data_preview(
    file_id: int,
    rows: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get preview of data file (first N rows)
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = await data_processing_engine.load_file_data(file_record)
        preview_data = data_processing_engine.get_sample_data(df, rows)
        
        return DataPreviewResponse(**preview_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")


@router.post("/query", response_model=DataOperationResponse)
async def query_data(
    query: DataQuery,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Execute data query with filtering, aggregation, and sorting
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, query.file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data
        df = await data_processing_engine.load_file_data(file_record)
        
        # Apply filters
        if query.filters:
            filter_conditions = [f.dict() for f in query.filters]
            df = data_processing_engine.filter_data(df, filter_conditions)
        
        # Apply aggregation
        if query.aggregation:
            df = data_processing_engine.aggregate_data(
                df, 
                query.aggregation.group_by, 
                query.aggregation.aggregations
            )
        
        # Apply sorting
        if query.sort_columns:
            sort_conditions = [s.dict() for s in query.sort_columns]
            df = data_processing_engine.sort_data(df, sort_conditions)
        
        # Apply limit
        if query.limit:
            df = df.head(query.limit)
        
        # Prepare response
        result_data = df.to_dict('records')
        columns = [{'name': col, 'type': str(df[col].dtype)} for col in df.columns]
        
        return DataOperationResponse(
            success=True,
            result_data=result_data,
            columns=columns,
            total_rows=len(df),
            message="Query executed successfully"
        )
        
    except Exception as e:
        return DataOperationResponse(
            success=False,
            error=f"Query execution failed: {str(e)}"
        )


@router.post("/{file_id}/filter", response_model=DataOperationResponse)
async def filter_data(
    file_id: int,
    filters: List[FilterCondition],
    limit: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Apply filters to data
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = await data_processing_engine.load_file_data(file_record)
        
        filter_conditions = [f.dict() for f in filters]
        filtered_df = data_processing_engine.filter_data(df, filter_conditions)
        
        if limit:
            filtered_df = filtered_df.head(limit)
        
        result_data = filtered_df.to_dict('records')
        columns = [{'name': col, 'type': str(filtered_df[col].dtype)} for col in filtered_df.columns]
        
        return DataOperationResponse(
            success=True,
            result_data=result_data,
            columns=columns,
            total_rows=len(filtered_df),
            message=f"Filter applied. {len(filtered_df)} rows returned"
        )
        
    except Exception as e:
        return DataOperationResponse(
            success=False,
            error=f"Filter operation failed: {str(e)}"
        )


@router.post("/{file_id}/aggregate", response_model=DataOperationResponse)
async def aggregate_data(
    file_id: int,
    aggregation: AggregationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Perform aggregation on data
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = await data_processing_engine.load_file_data(file_record)
        
        aggregated_df = data_processing_engine.aggregate_data(
            df, 
            aggregation.group_by, 
            aggregation.aggregations
        )
        
        result_data = aggregated_df.to_dict('records')
        columns = [{'name': col, 'type': str(aggregated_df[col].dtype)} for col in aggregated_df.columns]
        
        return DataOperationResponse(
            success=True,
            result_data=result_data,
            columns=columns,
            total_rows=len(aggregated_df),
            message=f"Aggregation completed. {len(aggregated_df)} groups returned"
        )
        
    except Exception as e:
        return DataOperationResponse(
            success=False,
            error=f"Aggregation failed: {str(e)}"
        )


@router.post("/{file_id}/sort", response_model=DataOperationResponse)
async def sort_data(
    file_id: int,
    sort_columns: List[SortColumn],
    limit: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Sort data by specified columns
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = await data_processing_engine.load_file_data(file_record)
        
        sort_conditions = [s.dict() for s in sort_columns]
        sorted_df = data_processing_engine.sort_data(df, sort_conditions)
        
        if limit:
            sorted_df = sorted_df.head(limit)
        
        result_data = sorted_df.to_dict('records')
        columns = [{'name': col, 'type': str(sorted_df[col].dtype)} for col in sorted_df.columns]
        
        return DataOperationResponse(
            success=True,
            result_data=result_data,
            columns=columns,
            total_rows=len(sorted_df),
            message="Data sorted successfully"
        )
        
    except Exception as e:
        return DataOperationResponse(
            success=False,
            error=f"Sort operation failed: {str(e)}"
        )


@router.delete("/{file_id}/cache")
async def clear_data_cache(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Clear cached data for a file
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    data_processing_engine.clear_cache(file_id)
    
    return {"message": "Cache cleared successfully"}