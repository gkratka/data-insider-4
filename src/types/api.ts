// File Upload Types
export interface FileUploadRequest {
  file: File;
  sessionId?: string;
}

export interface FileUploadResponse {
  fileId: string;
  filename: string;
  size: number;
  contentType: string;
  uploadedAt: string;
  sessionId: string;
  metadata: FileMetadata;
}

export interface FileMetadata {
  rows?: number;
  columns?: number;
  columnNames?: string[];
  columnTypes?: Record<string, string>;
  preview?: any[][];
}

// Session Types
export interface SessionResponse {
  sessionId: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
  files: FileUploadResponse[];
  isActive: boolean;
}

export interface CreateSessionRequest {
  userId?: string;
}

// Chat Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sessionId: string;
  metadata?: {
    fileReferences?: string[];
    queryType?: string;
    executionTime?: number;
  };
}

export interface SendMessageRequest {
  message: string;
  sessionId: string;
  fileIds?: string[];
}

export interface SendMessageResponse {
  messageId: string;
  response: ChatMessage;
  streamId?: string;
}

// Data Query Types
export interface DataQueryRequest {
  query: string;
  sessionId: string;
  fileIds: string[];
  parameters?: Record<string, any>;
}

export interface DataQueryResponse {
  queryId: string;
  result: {
    data?: any[][];
    columns?: string[];
    summary?: string;
    visualizations?: Visualization[];
    error?: string;
  };
  executionTime: number;
  metadata: {
    rowsAffected?: number;
    queryType: string;
    operations: string[];
  };
}

// Visualization Types
export interface Visualization {
  type: 'table' | 'bar' | 'line' | 'scatter' | 'histogram' | 'box' | 'heatmap';
  data: any;
  config: {
    title?: string;
    xAxis?: string;
    yAxis?: string;
    color?: string;
    [key: string]: any;
  };
}

// Data Processing Types
export interface ProcessDataRequest {
  fileId: string;
  operations: DataOperation[];
}

export interface DataOperation {
  type: 'filter' | 'sort' | 'aggregate' | 'transform' | 'merge';
  parameters: Record<string, any>;
}

export interface ProcessDataResponse {
  processedData: {
    data: any[][];
    columns: string[];
    metadata: {
      originalRows: number;
      processedRows: number;
      operations: string[];
    };
  };
}

// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  isActive: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
  expiresAt: string;
}

// Generic API Types
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface ApiErrorResponse {
  error: {
    message: string;
    code: string;
    details?: any;
  };
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface AsyncState<T> extends LoadingState {
  data: T | null;
}