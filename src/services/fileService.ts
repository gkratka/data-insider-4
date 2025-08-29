import { apiClient, handleApiError, ApiResponse } from '@/lib/api';
import { 
  FileUploadRequest, 
  FileUploadResponse, 
  ProcessDataRequest, 
  ProcessDataResponse 
} from '@/types/api';

class FileService {
  /**
   * Upload a file to the server
   */
  async uploadFile(request: FileUploadRequest): Promise<FileUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', request.file);
      
      if (request.sessionId) {
        formData.append('sessionId', request.sessionId);
      }

      const response = await apiClient.post<ApiResponse<FileUploadResponse>>(
        '/api/files/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 1)
            );
            // Emit progress event for UI updates
            window.dispatchEvent(
              new CustomEvent('fileUploadProgress', {
                detail: { filename: request.file.name, progress: percentCompleted }
              })
            );
          },
        }
      );

      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get file information by ID
   */
  async getFile(fileId: string): Promise<FileUploadResponse> {
    try {
      const response = await apiClient.get<ApiResponse<FileUploadResponse>>(
        `/api/files/${fileId}`
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get files for a session
   */
  async getSessionFiles(sessionId: string): Promise<FileUploadResponse[]> {
    try {
      const response = await apiClient.get<ApiResponse<FileUploadResponse[]>>(
        `/api/files/session/${sessionId}`
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Delete a file
   */
  async deleteFile(fileId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/files/${fileId}`);
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Process data with operations
   */
  async processData(request: ProcessDataRequest): Promise<ProcessDataResponse> {
    try {
      const response = await apiClient.post<ApiResponse<ProcessDataResponse>>(
        '/api/data/process',
        request
      );
      return response.data.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }

  /**
   * Get data preview for a file
   */
  async getDataPreview(fileId: string, limit: number = 100): Promise<any> {
    try {
      const response = await apiClient.get<ApiResponse<any>>(
        `/api/data/preview/${fileId}`,
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
   * Download processed data
   */
  async downloadData(
    fileId: string, 
    format: 'csv' | 'excel' | 'json' = 'csv'
  ): Promise<Blob> {
    try {
      const response = await apiClient.get(
        `/api/data/download/${fileId}`,
        {
          params: { format },
          responseType: 'blob'
        }
      );
      return response.data;
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }
}

export const fileService = new FileService();