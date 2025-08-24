import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import json

import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from app.core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class ClaudeAPIClient:
    """Anthropic Claude API client for conversational AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = "claude-3-sonnet-20240229"
        self.max_tokens = 4000
        self.temperature = 0.1
        
        # Rate limiting
        self.requests_per_minute = 50
        self.request_timestamps = []
    
    async def _check_rate_limit(self):
        """Check if we're within rate limits"""
        now = datetime.now()
        
        # Remove old timestamps (older than 1 minute)
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if (now - ts).total_seconds() < 60
        ]
        
        if len(self.request_timestamps) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_timestamps[0]).total_seconds()
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
        
        self.request_timestamps.append(now)
    
    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Create a completion using Claude API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Dict with completion response
        """
        await self._check_rate_limit()
        
        try:
            # Convert messages to proper format
            formatted_messages = []
            for msg in messages:
                formatted_messages.append(MessageParam(
                    role=msg['role'],
                    content=msg['content']
                ))
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature
            }
            
            if system_prompt:
                request_params["system"] = system_prompt
            
            if stream:
                return await self._create_streaming_completion(request_params)
            else:
                response = await self.client.messages.create(**request_params)
                
                return {
                    'id': response.id,
                    'content': response.content[0].text if response.content else '',
                    'usage': {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens
                    },
                    'finish_reason': response.stop_reason,
                    'model': response.model
                }
                
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    async def _create_streaming_completion(self, request_params: Dict) -> AsyncGenerator[Dict[str, Any], None]:
        """Create a streaming completion"""
        try:
            stream = await self.client.messages.create(
                stream=True,
                **request_params
            )
            
            async for chunk in stream:
                if hasattr(chunk, 'delta') and chunk.delta:
                    if hasattr(chunk.delta, 'text'):
                        yield {
                            'type': 'content_delta',
                            'content': chunk.delta.text,
                            'usage': None
                        }
                elif hasattr(chunk, 'message') and chunk.message:
                    yield {
                        'type': 'message_complete',
                        'content': '',
                        'usage': {
                            'input_tokens': chunk.message.usage.input_tokens if chunk.message.usage else 0,
                            'output_tokens': chunk.message.usage.output_tokens if chunk.message.usage else 0
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Streaming completion error: {str(e)}")
            yield {
                'type': 'error',
                'content': f"Streaming failed: {str(e)}",
                'usage': None
            }


class ConversationManager:
    """Manage conversation context and history"""
    
    def __init__(self, claude_client: ClaudeAPIClient):
        self.claude_client = claude_client
        self.conversations = {}  # session_id -> conversation history
        self.max_context_length = 8000  # tokens
    
    def create_conversation(self, session_id: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Create a new conversation"""
        self.conversations[session_id] = {
            'messages': [],
            'system_prompt': system_prompt,
            'created_at': datetime.now(),
            'token_count': 0
        }
        
        return {
            'session_id': session_id,
            'created_at': self.conversations[session_id]['created_at'],
            'message_count': 0
        }
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to conversation"""
        if session_id not in self.conversations:
            return False
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        }
        
        self.conversations[session_id]['messages'].append(message)
        
        # Estimate token count (rough approximation)
        self.conversations[session_id]['token_count'] += len(content.split()) * 1.3
        
        # Trim conversation if too long
        self._trim_conversation(session_id)
        
        return True
    
    def _trim_conversation(self, session_id: str):
        """Trim conversation to stay within context limits"""
        conversation = self.conversations[session_id]
        
        while conversation['token_count'] > self.max_context_length and len(conversation['messages']) > 2:
            # Remove oldest message (keep at least 2 messages for context)
            removed_message = conversation['messages'].pop(0)
            conversation['token_count'] -= len(removed_message['content'].split()) * 1.3
    
    async def get_completion(
        self,
        session_id: str,
        user_message: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Get Claude completion for a conversation"""
        if session_id not in self.conversations:
            return {'error': 'Conversation not found'}
        
        # Add user message
        self.add_message(session_id, 'user', user_message)
        
        conversation = self.conversations[session_id]
        
        # Prepare messages for API
        messages = []
        for msg in conversation['messages']:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        try:
            response = await self.claude_client.create_completion(
                messages=messages,
                system_prompt=conversation['system_prompt'],
                stream=stream
            )
            
            if not stream:
                # Add assistant response to conversation
                self.add_message(session_id, 'assistant', response['content'])
                
                return {
                    'session_id': session_id,
                    'response': response['content'],
                    'usage': response.get('usage'),
                    'message_count': len(conversation['messages'])
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Completion error for session {session_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_conversation_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history"""
        if session_id not in self.conversations:
            return None
        
        return [
            {
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': msg['timestamp'].isoformat()
            }
            for msg in self.conversations[session_id]['messages']
        ]
    
    def delete_conversation(self, session_id: str) -> bool:
        """Delete conversation"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False
    
    def get_conversation_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation statistics"""
        if session_id not in self.conversations:
            return None
        
        conversation = self.conversations[session_id]
        return {
            'session_id': session_id,
            'message_count': len(conversation['messages']),
            'token_count': conversation['token_count'],
            'created_at': conversation['created_at'].isoformat(),
            'last_message_at': conversation['messages'][-1]['timestamp'].isoformat() if conversation['messages'] else None
        }


# Global instances
claude_client = ClaudeAPIClient()
conversation_manager = ConversationManager(claude_client)