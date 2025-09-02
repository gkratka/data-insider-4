import { apiClient, handleApiError, ApiResponse } from '@/lib/api';
import { 
  ChatMessage, 
  SendMessageRequest, 
  SendMessageResponse,
  ChatResponse,
  DataQueryRequest,
  DataQueryResponse 
} from '@/types/api';

class ChatService {
  /**
   * Create a new conversation
   */
  async createConversation(sessionId: string, systemPrompt?: string): Promise<void> {
    try {
      await apiClient.post('/api/v1/chat/conversations', {
        session_id: sessionId,
        system_prompt: systemPrompt
      });
    } catch (error) {
      // Ignore errors - the backend will create conversations automatically
    }
  }

  /**
   * Send a message to the chat API
   */
  async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    try {
      const response = await apiClient.post<ChatResponse>(
        '/api/v1/chat',
        {
          message: request.message,
          session_id: request.sessionId,
          file_ids: request.fileIds || []
        }
      );
      return {
        id: Math.random().toString(36).substr(2, 9),
        content: response.data.response,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        sessionId: response.data.session_id
      };
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get chat history for a session
   */
  async getChatHistory(sessionId: string, limit: number = 50): Promise<ChatMessage[]> {
    try {
      const response = await apiClient.get<{session_id: string, messages: ChatMessage[]}>(
        `/api/v1/chat/conversations/${sessionId}/history`
      );
      return response.data.messages || [];
    } catch (error) {
      // If session doesn't exist, return empty array
      return [];
    }
  }

  /**
   * Stream messages - for now we'll use regular sendMessage and simulate streaming
   */
  async streamMessage(
    request: SendMessageRequest, 
    onMessage: (chunk: string) => void,
    onComplete: (message: ChatMessage) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      // Send regular message
      const response = await apiClient.post<ChatResponse>(
        '/api/v1/chat',
        {
          message: request.message,
          session_id: request.sessionId,
          file_ids: request.fileIds || []
        }
      );
      
      // Simulate streaming by sending chunks
      const fullResponse = response.data.response;
      const words = fullResponse.split(' ');
      
      for (let i = 0; i < words.length; i++) {
        const chunk = words[i] + (i < words.length - 1 ? ' ' : '');
        onMessage(chunk);
        await new Promise(resolve => setTimeout(resolve, 50)); // Small delay
      }
      
      // Complete the message
      onComplete({
        id: Math.random().toString(36).substr(2, 9),
        content: fullResponse,
        role: 'assistant',
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      const apiError = handleApiError(error);
      onError(apiError.message);
    }
  }

  /**
   * Execute a data query
   */
  async executeQuery(request: DataQueryRequest): Promise<DataQueryResponse> {
    try {
      const response = await apiClient.post<ApiResponse<DataQueryResponse>>(
        '/api/query/execute',
        request
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get query suggestions based on data context
   */
  async getQuerySuggestions(sessionId: string, fileIds: string[]): Promise<string[]> {
    try {
      const response = await apiClient.post<ApiResponse<string[]>>(
        '/api/query/suggestions',
        { sessionId, fileIds }
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Validate a query before execution
   */
  async validateQuery(query: string, fileIds: string[]): Promise<{ isValid: boolean; issues?: string[] }> {
    try {
      const response = await apiClient.post<ApiResponse<{ isValid: boolean; issues?: string[] }>>(
        '/api/query/validate',
        { query, fileIds }
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get message by ID
   */
  async getMessage(messageId: string): Promise<ChatMessage> {
    try {
      const response = await apiClient.get<ApiResponse<ChatMessage>>(
        `/api/chat/message/${messageId}`
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Delete a message
   */
  async deleteMessage(messageId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/chat/message/${messageId}`);
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Clear chat history for a session
   */
  async clearChatHistory(sessionId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/chat/history/${sessionId}`);
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }
}

export const chatService = new ChatService();