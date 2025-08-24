from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.query import NaturalLanguageQuery, QueryResponse, QuerySuggestion
from app.services.query_processor import query_processor
from app.services.file_service import FileService
from app.services.data_processing_service import data_processing_engine
from app.auth.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()
file_service = FileService()


@router.post("/natural-language", response_model=QueryResponse)
async def process_natural_language_query(
    nl_query: NaturalLanguageQuery,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Process a natural language query against a data file
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, nl_query.file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = await query_processor.process_query(
            query=nl_query.query,
            file_record=file_record,
            session_id=nl_query.session_id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.get("/{file_id}/suggestions", response_model=List[QuerySuggestion])
async def get_query_suggestions(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get suggested queries for a data file based on its structure
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data summary to generate suggestions
        df = await data_processing_engine.load_file_data(file_record)
        data_summary = data_processing_engine.get_data_summary(df)
        
        suggestions = []
        columns = data_summary.get('columns', [])
        numeric_cols = [col for col, dtype in data_summary.get('dtypes', {}).items() if 'int' in dtype or 'float' in dtype]
        categorical_cols = [col for col, dtype in data_summary.get('dtypes', {}).items() if dtype == 'object']
        
        # Basic exploration suggestions
        suggestions.extend([
            QuerySuggestion(
                suggestion="Get data summary",
                intent="summarize",
                description="Show basic statistics and overview of the dataset",
                example_query="Show me a summary of this data"
            ),
            QuerySuggestion(
                suggestion="Preview data",
                intent="filter",
                description="Display the first few rows of data",
                example_query="Show me the first 10 rows"
            )
        ])
        
        # Column-specific suggestions
        if numeric_cols:
            col = numeric_cols[0]
            suggestions.extend([
                QuerySuggestion(
                    suggestion=f"Analyze {col}",
                    intent="statistics",
                    description=f"Get statistics for the {col} column",
                    example_query=f"What are the statistics for {col}?"
                ),
                QuerySuggestion(
                    suggestion=f"Filter by {col}",
                    intent="filter",
                    description=f"Filter data based on {col} values",
                    example_query=f"Show me rows where {col} is greater than 100"
                )
            ])
        
        if categorical_cols:
            col = categorical_cols[0]
            suggestions.extend([
                QuerySuggestion(
                    suggestion=f"Count by {col}",
                    intent="aggregate",
                    description=f"Count occurrences of each {col} value",
                    example_query=f"How many of each {col} are there?"
                ),
                QuerySuggestion(
                    suggestion=f"Group by {col}",
                    intent="aggregate",
                    description=f"Group data by {col} categories",
                    example_query=f"Group the data by {col}"
                )
            ])
        
        # Multi-column suggestions
        if len(columns) >= 2:
            col1, col2 = columns[0], columns[1]
            suggestions.append(
                QuerySuggestion(
                    suggestion=f"Compare {col1} and {col2}",
                    intent="statistics",
                    description=f"Analyze relationship between {col1} and {col2}",
                    example_query=f"Show me the relationship between {col1} and {col2}"
                )
            )
        
        # Sort suggestions
        if numeric_cols:
            col = numeric_cols[0]
            suggestions.append(
                QuerySuggestion(
                    suggestion=f"Top values by {col}",
                    intent="sort",
                    description=f"Show highest {col} values",
                    example_query=f"Show me the top 10 rows sorted by {col}"
                )
            )
        
        return suggestions[:8]  # Limit to 8 suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")


@router.post("/{file_id}/validate-query")
async def validate_query(
    file_id: int,
    query: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Validate a natural language query without executing it
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data summary for validation
        df = await data_processing_engine.load_file_data(file_record)
        data_summary = data_processing_engine.get_data_summary(df)
        
        # Classify intent and extract entities
        intent = query_processor.nlp.classify_intent(query)
        entities = query_processor.nlp.extract_entities(query, data_summary['columns'])
        
        # Check for issues
        issues = []
        
        # Check if referenced columns exist
        for col in entities.get('columns', []):
            if col not in data_summary['columns']:
                issues.append(f"Column '{col}' not found in dataset")
        
        # Check if intent is clear
        if intent.value == 'unknown':
            issues.append("Query intent is unclear. Try using more specific keywords.")
        
        # Check if necessary entities are present
        if intent.value == 'filter' and not entities.get('columns'):
            issues.append("Filter queries need column names")
        
        if intent.value == 'aggregate' and not entities.get('columns'):
            issues.append("Aggregation queries need column names")
        
        return {
            'valid': len(issues) == 0,
            'intent': intent.value,
            'entities': entities,
            'issues': issues,
            'suggestions': [
                "Be more specific about which columns to use",
                "Use clear keywords like 'filter', 'count', 'average', etc.",
                f"Available columns: {', '.join(data_summary['columns'][:5])}{'...' if len(data_summary['columns']) > 5 else ''}"
            ] if issues else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query validation failed: {str(e)}")


@router.get("/{file_id}/example-queries")
async def get_example_queries(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get example queries specific to the data file
    """
    user_id = current_user.id if current_user else None
    file_record = file_service.get_file_by_id(db, file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data to generate context-specific examples
        df = await data_processing_engine.load_file_data(file_record)
        data_summary = data_processing_engine.get_data_summary(df)
        
        columns = data_summary.get('columns', [])
        examples = []
        
        if columns:
            # Use actual column names in examples
            col1 = columns[0]
            
            examples = [
                f"Show me the first 20 rows",
                f"What is the summary of this data?",
                f"Filter rows where {col1} contains 'value'",
                f"Sort data by {col1}",
                f"Count the number of rows"
            ]
            
            # Add more specific examples based on column types
            numeric_cols = [col for col, dtype in data_summary.get('dtypes', {}).items() 
                          if 'int' in dtype or 'float' in dtype]
            
            if numeric_cols:
                col = numeric_cols[0]
                examples.extend([
                    f"What is the average {col}?",
                    f"Show me rows where {col} is greater than 100",
                    f"What are the statistics for {col}?"
                ])
            
            categorical_cols = [col for col, dtype in data_summary.get('dtypes', {}).items() 
                              if dtype == 'object']
            
            if categorical_cols:
                col = categorical_cols[0]
                examples.extend([
                    f"How many different {col} values are there?",
                    f"Group data by {col}",
                    f"Count occurrences of each {col}"
                ])
        
        return {
            'examples': examples[:10],  # Limit to 10 examples
            'file_info': {
                'columns': columns,
                'row_count': data_summary.get('shape', [0])[0] if data_summary.get('shape') else 0,
                'column_count': len(columns)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate examples: {str(e)}")