import { apiClient, handleApiError, ApiResponse } from '@/lib/api';
import { 
  ChatMessage, 
  SendMessageRequest, 
  SendMessageResponse,
  DataQueryRequest,
  DataQueryResponse 
} from '@/types/api';

class ChatService {
  /**
   * Send a message to the chat API
   */
  async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    try {
      const response = await apiClient.post<ApiResponse<SendMessageResponse>>(
        '/api/chat/message',
        request
      );
      return response.data.data;
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
      const response = await apiClient.get<ApiResponse<ChatMessage[]>>(
        `/api/chat/history/${sessionId}`,
        {
          params: { limit }
        }
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Stream messages using Server-Sent Events
   */
  async streamMessage(
    request: SendMessageRequest, 
    onMessage: (chunk: string) => void,
    onComplete: (message: ChatMessage) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const response = await apiClient.post<ApiResponse<{ streamId: string }>>(
        '/api/chat/stream',
        request
      );
      
      const { streamId } = response.data.data;
      
      // Create EventSource for streaming
      const eventSource = new EventSource(`${apiClient.defaults.baseURL}/api/chat/stream/${streamId}`);
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
          onMessage(data.content);
        } else if (data.type === 'complete') {
          onComplete(data.message);
          eventSource.close();
        } else if (data.type === 'error') {
          onError(data.error);
          eventSource.close();
        }
      };
      
      eventSource.onerror = () => {
        onError('Connection error occurred');
        eventSource.close();
      };
      
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