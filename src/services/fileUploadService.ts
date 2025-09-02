/**
 * File upload service for communicating with backend
 */

import { apiClient } from '@/lib/api';

export interface BackendFileResponse {
  filename: string;
  size: number;
  content_type: string;
  file_id: string;
  message: string;
}

export interface MultipleUploadResponse {
  message: string;
  files: BackendFileResponse[];
}

class FileUploadService {
  /**
   * Upload a single file to the backend
   */
  async uploadFile(file: File): Promise<BackendFileResponse> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post<BackendFileResponse>('/api/v1/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds for large files
      });

      return response.data;
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 413) {
        throw new Error('File too large. Maximum size is 500MB.');
      } else if (error.response?.status === 400) {
        throw new Error(error.response.data?.detail || 'Invalid file format.');
      } else if (error.response?.status === 500) {
        throw new Error('Server error during upload. Please try again.');
      } else {
        throw new Error('Upload failed. Please check your connection and try again.');
      }
    }
  }

  /**
   * Upload multiple files to the backend
   */
  async uploadMultipleFiles(files: File[]): Promise<MultipleUploadResponse> {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await apiClient.post<MultipleUploadResponse>('/api/v1/files/upload-multiple', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes for multiple files
      });

      return response.data;
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 413) {
        throw new Error('One or more files are too large. Maximum size is 500MB per file.');
      } else if (error.response?.status === 400) {
        throw new Error(error.response.data?.detail || 'One or more files have invalid format.');
      } else if (error.response?.status === 500) {
        throw new Error('Server error during upload. Please try again.');
      } else {
        throw new Error('Upload failed. Please check your connection and try again.');
      }
    }
  }

  /**
   * List uploaded files
   */
  async listFiles(): Promise<{ files: Array<{ filename: string; size: number; uploaded_at: number; file_id: string }> }> {
    try {
      const response = await apiClient.get('/api/v1/files');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch file list');
    }
  }

  /**
   * Delete a file
   */
  async deleteFile(fileId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/files/${fileId}`);
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('File not found');
      } else {
        throw new Error('Failed to delete file');
      }
    }
  }

  /**
   * Upload file with progress tracking
   */
  async uploadFileWithProgress(
    file: File,
    onProgress: (progress: number) => void
  ): Promise<BackendFileResponse> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post<BackendFileResponse>('/api/v1/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });

      return response.data;
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 413) {
        throw new Error('File too large. Maximum size is 500MB.');
      } else if (error.response?.status === 400) {
        throw new Error(error.response.data?.detail || 'Invalid file format.');
      } else if (error.response?.status === 500) {
        throw new Error('Server error during upload. Please try again.');
      } else {
        throw new Error('Upload failed. Please check your connection and try again.');
      }
    }
  }
}

// Export singleton instance
export const fileUploadService = new FileUploadService();
export { FileUploadService };