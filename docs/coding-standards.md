# Coding Standards

## Overview

This document establishes coding standards and best practices for the Data Intelligence Platform. Following these guidelines ensures code consistency, maintainability, and team collaboration effectiveness.

## General Principles

### Code Quality
- **Readability**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns and conventions throughout the codebase
- **Simplicity**: Prefer simple, clear solutions over complex ones
- **Performance**: Write efficient code without premature optimization
- **Security**: Always consider security implications in code design

### Documentation
- Write clear, concise comments for complex logic
- Maintain up-to-date README files
- Document API endpoints and interfaces
- Include examples in documentation

## Frontend Standards (React/TypeScript)

### File Organization

**Directory Structure**:
```
src/
├── components/
│   ├── ui/              # shadcn/ui components (auto-generated)
│   ├── Chat/           # Feature-specific components
│   ├── DataUpload/     # Feature-specific components
│   └── shared/         # Reusable components
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
├── pages/              # Route components
├── services/           # API clients
├── types/              # TypeScript type definitions
└── utils/              # Helper functions
```

**File Naming Conventions**:
- Components: `PascalCase.tsx` (e.g., `ChatInterface.tsx`)
- Hooks: `camelCase.ts` with `use` prefix (e.g., `useDataUpload.ts`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`)
- Types: `camelCase.ts` with descriptive names (e.g., `chatTypes.ts`)

### React Component Standards

**Component Structure**:
```tsx
import React from 'react';
import { ComponentProps } from './ComponentName.types';
import { Card } from '@/components/ui/card';
import { useComponentLogic } from './useComponentLogic';

/**
 * ComponentName description
 * @param props - Component properties
 * @returns JSX element
 */
export const ComponentName: React.FC<ComponentProps> = ({
  requiredProp,
  optionalProp = 'defaultValue',
  ...restProps
}) => {
  const { state, handlers } = useComponentLogic({ requiredProp });

  return (
    <Card className="component-container" {...restProps}>
      {/* Component content */}
    </Card>
  );
};

export default ComponentName;
```

**Component Guidelines**:
- Use functional components with hooks
- Extract complex logic into custom hooks
- Use TypeScript interfaces for props
- Implement proper error boundaries
- Use `React.memo` for performance optimization when needed
- Prefer composition over inheritance

### TypeScript Standards

**Type Definitions**:
```tsx
// Define interfaces for component props
interface ComponentProps {
  id: string;
  title: string;
  isActive?: boolean;
  onClick?: (id: string) => void;
  children?: React.ReactNode;
}

// Use discriminated unions for state management
type LoadingState = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: any }
  | { status: 'error'; error: string };

// Define API response types
interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

// Use enums for constants
enum FileStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}
```

**TypeScript Best Practices**:
- Use strict TypeScript configuration
- Prefer interfaces over types for object shapes
- Use union types for state management
- Avoid `any` type; use `unknown` when necessary
- Implement proper error types
- Use generics for reusable components

### React Hooks Standards

**Custom Hook Pattern**:
```tsx
import { useState, useEffect, useCallback } from 'react';

interface UseDataUploadOptions {
  onSuccess?: (files: File[]) => void;
  onError?: (error: string) => void;
}

interface UseDataUploadReturn {
  files: File[];
  isUploading: boolean;
  error: string | null;
  uploadFiles: (files: File[]) => Promise<void>;
  removeFile: (index: number) => void;
  clearFiles: () => void;
}

export const useDataUpload = (
  options: UseDataUploadOptions = {}
): UseDataUploadReturn => {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadFiles = useCallback(async (newFiles: File[]) => {
    setIsUploading(true);
    setError(null);
    
    try {
      // Upload logic here
      setFiles(prev => [...prev, ...newFiles]);
      options.onSuccess?.(newFiles);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      options.onError?.(errorMessage);
    } finally {
      setIsUploading(false);
    }
  }, [options]);

  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
    setError(null);
  }, []);

  return {
    files,
    isUploading,
    error,
    uploadFiles,
    removeFile,
    clearFiles
  };
};
```

### State Management

**Local State with useState**:
```tsx
// Simple state
const [isOpen, setIsOpen] = useState(false);

// Complex state with useReducer
interface State {
  data: any[];
  loading: boolean;
  error: string | null;
}

type Action = 
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: any[] }
  | { type: 'FETCH_ERROR'; payload: string };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, data: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
};
```

**Global State with Zustand**:
```tsx
import { create } from 'zustand';

interface AppState {
  user: User | null;
  session: Session | null;
  setUser: (user: User | null) => void;
  setSession: (session: Session | null) => void;
  clearState: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  session: null,
  setUser: (user) => set({ user }),
  setSession: (session) => set({ session }),
  clearState: () => set({ user: null, session: null })
}));
```

### CSS and Styling Standards

**Tailwind CSS Guidelines**:
```tsx
// Use semantic class organization
<div className={cn(
  // Layout
  "flex items-center justify-between",
  // Spacing
  "px-4 py-2 gap-2",
  // Appearance
  "bg-white border rounded-lg shadow-sm",
  // States
  "hover:shadow-md focus:outline-none focus:ring-2",
  // Responsive
  "md:px-6 lg:py-3",
  // Conditional classes
  isActive && "bg-blue-50 border-blue-200",
  className
)}>
```

**Component Styling Pattern**:
```tsx
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
```

## Backend Standards (Python/FastAPI)

### File Organization

**Directory Structure**:
```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/      # API route handlers
│   │   ├── dependencies/   # Dependency injection
│   │   └── middleware/     # Custom middleware
│   ├── core/
│   │   ├── config.py      # Configuration settings
│   │   ├── security.py    # Security utilities
│   │   └── database.py    # Database connection
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── tests/                 # Test files
└── migrations/            # Database migrations
```

### Python Code Standards

**Import Organization**:
```python
# Standard library imports
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local imports
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
```

**Function and Class Standards**:
```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DataProcessingService:
    """Service for processing uploaded data files."""
    
    def __init__(self, session: Session):
        self.session = session
        
    async def process_file(
        self, 
        file_content: bytes, 
        filename: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process uploaded file and return analysis results.
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename with extension
            user_id: ID of the user uploading the file
            
        Returns:
            Dictionary containing processed data and metadata
            
        Raises:
            ValueError: If file format is not supported
            ProcessingError: If file processing fails
        """
        try:
            # Validate file format
            if not self._is_supported_format(filename):
                raise ValueError(f"Unsupported file format: {filename}")
            
            # Process file content
            data = self._parse_file_content(file_content, filename)
            
            # Generate metadata
            metadata = self._generate_metadata(data, filename)
            
            logger.info(
                "File processed successfully",
                extra={
                    "filename": filename,
                    "user_id": user_id,
                    "rows": len(data),
                    "columns": len(data.columns) if hasattr(data, 'columns') else 0
                }
            )
            
            return {
                "data": data.to_dict(orient="records"),
                "metadata": metadata,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(
                "File processing failed",
                extra={
                    "filename": filename,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise ProcessingError(f"Failed to process file: {str(e)}")
    
    def _is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported."""
        supported_extensions = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
        return any(filename.lower().endswith(ext) for ext in supported_extensions)
```

### API Endpoint Standards

**FastAPI Route Pattern**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.query import QueryRequest, QueryResponse
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/v1/query", tags=["query"])

@router.post("/process", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service)
) -> QueryResponse:
    """
    Process a natural language query and return results.
    
    - **session_id**: ID of the data session
    - **query**: Natural language query string
    - **context**: Optional context from previous queries
    """
    try:
        # Validate session ownership
        session = db.query(DataSession).filter(
            DataSession.id == request.session_id,
            DataSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Process query
        result = await llm_service.process_query(
            query=request.query,
            session=session,
            context=request.context
        )
        
        return QueryResponse(
            query_id=result.id,
            result=result.data,
            explanation=result.explanation,
            execution_time=result.execution_time
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Query processing failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### Database Model Standards

**SQLAlchemy Model Pattern**:
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class DataSession(Base, TimestampMixin):
    """Model for user data analysis sessions."""
    
    __tablename__ = "data_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    metadata = Column(JSONB, default=dict, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    files = relationship("DataFile", back_populates="session", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<DataSession(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }
```

### Pydantic Schema Standards

**Schema Pattern**:
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QueryStatus(str, Enum):
    """Enumeration for query status values."""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class QueryRequest(BaseModel):
    """Schema for query processing requests."""
    
    session_id: str = Field(..., description="ID of the data session")
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    context: Optional[Dict[str, Any]] = Field(None, description="Previous query context")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate query string."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

class QueryResponse(BaseModel):
    """Schema for query processing responses."""
    
    query_id: str = Field(..., description="Unique query identifier")
    status: QueryStatus = Field(..., description="Query processing status")
    result: Optional[Dict[str, Any]] = Field(None, description="Query results")
    explanation: Optional[str] = Field(None, description="Natural language explanation")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## Error Handling Standards

### Frontend Error Handling

**Error Boundary Pattern**:
```tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>Please refresh the page and try again.</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**API Error Handling**:
```tsx
import { useQuery } from '@tanstack/react-query';

interface ApiError {
  message: string;
  code: string;
  details?: any;
}

const useDataQuery = (sessionId: string) => {
  return useQuery({
    queryKey: ['data', sessionId],
    queryFn: async () => {
      const response = await fetch(`/api/data/${sessionId}`);
      
      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.message || 'Request failed');
      }
      
      return response.json();
    },
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error.message.includes('400') || error.message.includes('401')) {
        return false;
      }
      return failureCount < 3;
    },
    onError: (error) => {
      console.error('Query failed:', error);
      // Show user-friendly error message
    }
  });
};
```

### Backend Error Handling

**Custom Exception Classes**:
```python
class DataIntelligenceException(Exception):
    """Base exception class for the application."""
    
    def __init__(self, message: str, code: str = "GENERIC_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ValidationError(DataIntelligenceException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")

class ProcessingError(DataIntelligenceException):
    """Exception for data processing errors."""
    
    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        super().__init__(message, "PROCESSING_ERROR")

class LLMServiceError(DataIntelligenceException):
    """Exception for LLM service errors."""
    
    def __init__(self, message: str, provider: str = None):
        self.provider = provider
        super().__init__(message, "LLM_SERVICE_ERROR")
```

**Global Exception Handler**:
```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the FastAPI application."""
    
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "request_id": request_id
                }
            }
        )
    
    elif isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "request_id": request_id
                }
            }
        )
    
    elif isinstance(exc, DataIntelligenceException):
        logger.warning(f"Application error: {exc.message}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request_id
                }
            }
        )
    
    else:
        logger.exception(f"Unhandled exception: {str(exc)}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "request_id": request_id
                }
            }
        )
```

## Testing Standards

### Frontend Testing

**Component Test Pattern**:
```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ChatInterface } from './ChatInterface';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
});

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('ChatInterface', () => {
  it('should render chat input', () => {
    renderWithProviders(<ChatInterface />);
    expect(screen.getByPlaceholderText('Ask Gemini')).toBeInTheDocument();
  });

  it('should send message on Enter key', async () => {
    const mockOnSend = jest.fn();
    renderWithProviders(<ChatInterface onSendMessage={mockOnSend} />);
    
    const input = screen.getByPlaceholderText('Ask Gemini');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(mockOnSend).toHaveBeenCalledWith('Test message');
    });
  });
});
```

### Backend Testing

**API Test Pattern**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    return response.json()

class TestQueryEndpoints:
    def test_process_query_success(self, client, test_user):
        # Login and get token
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        # Create session and upload file
        # ... setup code
        
        # Test query processing
        query_data = {
            "session_id": "test-session-id",
            "query": "Show me sales by region"
        }
        response = client.post(
            "/api/v1/query/process",
            json=query_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "query_id" in data
        assert "result" in data
    
    def test_process_query_invalid_session(self, client, test_user):
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com", 
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        query_data = {
            "session_id": "invalid-session-id",
            "query": "Show me data"
        }
        response = client.post(
            "/api/v1/query/process",
            json=query_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
```

## Documentation Standards

### Code Documentation

**Docstring Standards** (Python):
```python
def process_data_file(
    file_content: bytes,
    filename: str,
    options: Dict[str, Any] = None
) -> ProcessingResult:
    """
    Process uploaded data file and return structured results.
    
    This function handles multiple file formats (CSV, Excel, JSON, Parquet)
    and performs initial data validation and type inference.
    
    Args:
        file_content: Raw file content as bytes
        filename: Original filename with extension for format detection
        options: Optional processing parameters including:
            - delimiter: Custom delimiter for CSV files
            - sheet_name: Specific sheet for Excel files
            - encoding: Text encoding override
    
    Returns:
        ProcessingResult containing:
            - data: Processed DataFrame as dict
            - metadata: File statistics and schema info
            - validation_errors: List of data quality issues
    
    Raises:
        ValidationError: If file format is unsupported or corrupted
        ProcessingError: If data processing fails
        
    Example:
        >>> with open('sales.csv', 'rb') as f:
        ...     content = f.read()
        >>> result = process_data_file(content, 'sales.csv')
        >>> print(f"Processed {len(result.data)} rows")
    """
```

**JSDoc Standards** (TypeScript):
```tsx
/**
 * Custom hook for managing file upload state and operations
 * 
 * @param options - Configuration options for upload behavior
 * @param options.maxFiles - Maximum number of files allowed
 * @param options.maxSize - Maximum file size in bytes
 * @param options.onSuccess - Callback fired on successful upload
 * @param options.onError - Callback fired on upload error
 * 
 * @returns Object containing upload state and control functions
 * 
 * @example
 * ```tsx
 * const { uploadFiles, files, isUploading } = useFileUpload({
 *   maxFiles: 5,
 *   maxSize: 50 * 1024 * 1024, // 50MB
 *   onSuccess: (files) => console.log('Uploaded:', files)
 * });
 * ```
 */
export const useFileUpload = (options: UseFileUploadOptions = {}) => {
  // Implementation
};
```

## Performance Standards

### Frontend Performance

**Code Splitting**:
```tsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const DataVisualization = lazy(() => import('./DataVisualization'));
const AdvancedAnalytics = lazy(() => import('./AdvancedAnalytics'));

export const App = () => (
  <Router>
    <Routes>
      <Route path="/visualize" element={
        <Suspense fallback={<LoadingSpinner />}>
          <DataVisualization />
        </Suspense>
      } />
    </Routes>
  </Router>
);
```

**Memoization**:
```tsx
import { memo, useMemo, useCallback } from 'react';

interface DataTableProps {
  data: any[];
  onRowSelect: (id: string) => void;
}

export const DataTable = memo<DataTableProps>(({ data, onRowSelect }) => {
  const processedData = useMemo(() => {
    return data.map(row => ({
      ...row,
      displayValue: formatCurrency(row.value)
    }));
  }, [data]);

  const handleRowClick = useCallback((row: any) => {
    onRowSelect(row.id);
  }, [onRowSelect]);

  return (
    <table>
      {processedData.map(row => (
        <tr key={row.id} onClick={() => handleRowClick(row)}>
          {/* Table content */}
        </tr>
      ))}
    </table>
  );
});
```

### Backend Performance

**Database Query Optimization**:
```python
from sqlalchemy.orm import selectinload, joinedload

class QueryService:
    def get_session_with_files(self, session_id: str) -> DataSession:
        """Efficiently load session with related files using eager loading."""
        return self.db.query(DataSession)\
            .options(
                selectinload(DataSession.files),
                joinedload(DataSession.user)
            )\
            .filter(DataSession.id == session_id)\
            .first()
    
    def get_paginated_queries(
        self, 
        session_id: str, 
        offset: int = 0, 
        limit: int = 50
    ) -> List[Query]:
        """Get queries with pagination to avoid loading large result sets."""
        return self.db.query(Query)\
            .filter(Query.session_id == session_id)\
            .order_by(Query.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
```

**Async Processing**:
```python
import asyncio
from typing import List
import aiohttp

class LLMService:
    async def process_batch_queries(
        self, 
        queries: List[str]
    ) -> List[QueryResult]:
        """Process multiple queries concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._process_single_query(session, query) 
                for query in queries
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        return [
            result if not isinstance(result, Exception) else None
            for result in results
        ]
```

These coding standards provide a comprehensive foundation for maintaining high-quality, consistent code across the Data Intelligence Platform. All team members should follow these guidelines and update them as the project evolves.