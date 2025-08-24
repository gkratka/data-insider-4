from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = False


class ChatResponse(BaseModel):
    session_id: str
    response: str
    usage: Optional[Dict[str, int]] = None
    message_count: int
    timestamp: str = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        super().__init__(**data)


class ConversationCreate(BaseModel):
    session_id: str
    system_prompt: Optional[str] = None


class ConversationResponse(BaseModel):
    session_id: str
    created_at: str
    message_count: int


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]


class ConversationStats(BaseModel):
    session_id: str
    message_count: int
    token_count: float
    created_at: str
    last_message_at: Optional[str] = None


class StreamChunk(BaseModel):
    type: str  # 'content_delta', 'message_complete', 'error'
    content: str
    usage: Optional[Dict[str, int]] = None