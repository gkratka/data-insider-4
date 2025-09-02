import { apiClient, handleApiError, ApiResponse } from '@/lib/api';
import { SessionResponse, CreateSessionRequest } from '@/types/api';

class SessionService {
  private currentSessionId: string | null = null;

  /**
   * Create a new session
   */
  async createSession(request?: CreateSessionRequest): Promise<SessionResponse> {
    try {
      const response = await apiClient.post<ApiResponse<SessionResponse>>(
        '/api/sessions',
        request || {}
      );
      
      const session = response.data.data;
      this.currentSessionId = session.sessionId;
      
      // Store session ID in localStorage
      localStorage.setItem('currentSessionId', session.sessionId);
      
      return session;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get session by ID
   */
  async getSession(sessionId: string): Promise<SessionResponse> {
    try {
      const response = await apiClient.get<ApiResponse<SessionResponse>>(
        `/api/sessions/${sessionId}`
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get current session
   */
  async getCurrentSession(): Promise<SessionResponse> {
    const sessionId = this.getCurrentSessionId();
    if (!sessionId) {
      return await this.createSession();
    }
    
    try {
      return await this.getSession(sessionId);
    } catch (error) {
      // If session doesn't exist, create a new one
      return await this.createSession();
    }
  }

  /**
   * Update session
   */
  async updateSession(sessionId: string, updates: Partial<SessionResponse>): Promise<SessionResponse> {
    try {
      const response = await apiClient.put<ApiResponse<SessionResponse>>(
        `/api/sessions/${sessionId}`,
        updates
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Delete session
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/sessions/${sessionId}`);
      
      // Clear current session if it's the one being deleted
      if (this.currentSessionId === sessionId) {
        this.currentSessionId = null;
        localStorage.removeItem('currentSessionId');
      }
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get all sessions for current user
   */
  async getUserSessions(): Promise<SessionResponse[]> {
    try {
      const response = await apiClient.get<ApiResponse<SessionResponse[]>>(
        '/api/sessions'
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get current session ID
   */
  getCurrentSessionId(): string | null {
    if (this.currentSessionId) {
      return this.currentSessionId;
    }
    
    const storedSessionId = localStorage.getItem('currentSessionId');
    if (storedSessionId) {
      this.currentSessionId = storedSessionId;
      return storedSessionId;
    }
    
    return null;
  }

  /**
   * Set current session ID
   */
  setCurrentSessionId(sessionId: string): void {
    this.currentSessionId = sessionId;
    localStorage.setItem('currentSessionId', sessionId);
  }

  /**
   * Clear current session
   */
  clearCurrentSession(): void {
    this.currentSessionId = null;
    localStorage.removeItem('currentSessionId');
  }

  /**
   * Check if session is active
   */
  async isSessionActive(sessionId: string): Promise<boolean> {
    try {
      const session = await this.getSession(sessionId);
      return session.isActive;
    } catch (error) {
      return false;
    }
  }
}

export const sessionService = new SessionService();