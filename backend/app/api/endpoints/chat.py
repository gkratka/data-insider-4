from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio

from app.database import get_db
from app.schemas.claude import (
    ChatRequest, ChatResponse, ConversationCreate, ConversationResponse,
    ConversationHistory, ConversationStats, StreamChunk
)
from app.services.claude_service import conversation_manager
from app.auth.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_create: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Create a new conversation with Claude
    """
    try:
        # Default system prompt for data analysis
        default_system_prompt = """You are an expert data analyst assistant. You help users analyze and understand their data through natural language queries. 

Key capabilities:
- Interpret natural language queries about data
- Suggest appropriate data operations (filtering, aggregation, visualization)
- Explain data insights in clear, non-technical language
- Guide users through complex data analysis workflows
- Provide actionable recommendations based on data

Always be concise, accurate, and helpful. Ask clarifying questions when queries are ambiguous."""
        
        system_prompt = conversation_create.system_prompt or default_system_prompt
        
        conversation_info = conversation_manager.create_conversation(
            session_id=conversation_create.session_id,
            system_prompt=system_prompt
        )
        
        return ConversationResponse(
            session_id=conversation_info['session_id'],
            created_at=conversation_info['created_at'].isoformat(),
            message_count=conversation_info['message_count']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_claude(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Send a message to Claude and get a response
    """
    try:
        response = await conversation_manager.get_completion(
            session_id=chat_request.session_id,
            user_message=chat_request.message,
            stream=False
        )
        
        if 'error' in response:
            raise HTTPException(status_code=500, detail=response['error'])
        
        return ChatResponse(
            session_id=response['session_id'],
            response=response['response'],
            usage=response.get('usage'),
            message_count=response['message_count']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/chat/stream")
async def chat_with_claude_stream(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Send a message to Claude and get a streaming response
    """
    async def generate_stream():
        try:
            response_stream = await conversation_manager.get_completion(
                session_id=chat_request.session_id,
                user_message=chat_request.message,
                stream=True
            )
            
            if 'error' in response_stream:
                yield f"data: {json.dumps({'error': response_stream['error']})}\n\n"
                return
            
            full_response = ""
            
            async for chunk in response_stream:
                chunk_data = StreamChunk(**chunk)
                yield f"data: {json.dumps(chunk_data.dict())}\n\n"
                
                if chunk_data.type == 'content_delta':
                    full_response += chunk_data.content
                elif chunk_data.type == 'message_complete':
                    # Add assistant response to conversation
                    conversation_manager.add_message(
                        chat_request.session_id, 
                        'assistant', 
                        full_response
                    )
                    break
                    
        except Exception as e:
            error_chunk = StreamChunk(
                type='error',
                content=f"Streaming error: {str(e)}",
                usage=None
            )
            yield f"data: {json.dumps(error_chunk.dict())}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.get("/conversations/{session_id}/history", response_model=ConversationHistory)
async def get_conversation_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get conversation history
    """
    history = conversation_manager.get_conversation_history(session_id)
    
    if history is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationHistory(
        session_id=session_id,
        messages=history
    )


@router.get("/conversations/{session_id}/stats", response_model=ConversationStats)
async def get_conversation_stats(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get conversation statistics
    """
    stats = conversation_manager.get_conversation_stats(session_id)
    
    if stats is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationStats(**stats)


@router.delete("/conversations/{session_id}")
async def delete_conversation(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Delete a conversation
    """
    success = conversation_manager.delete_conversation(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation deleted successfully"}