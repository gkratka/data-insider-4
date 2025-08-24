# Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the Data Intelligence Platform, ensuring code quality, reliability, and user satisfaction through systematic testing approaches.

## Testing Philosophy

### Core Principles
- **Test-Driven Development**: Write tests before implementation when possible
- **Comprehensive Coverage**: Aim for high test coverage across all components
- **Realistic Testing**: Use real-world scenarios and data in tests
- **Fast Feedback**: Prioritize quick test execution for rapid development cycles
- **Maintainable Tests**: Write clear, readable tests that serve as documentation

### Testing Pyramid
```
                 /\
                /  \
               /E2E \
              /______\
             /        \
            /Integration\
           /__________\
          /            \
         /   Unit Tests  \
        /________________\
```

**Unit Tests (70%)**: Fast, isolated tests for individual functions and components  
**Integration Tests (20%)**: Tests for component interactions and API endpoints  
**End-to-End Tests (10%)**: Full user workflow testing across the entire application

## Frontend Testing Strategy

### Testing Stack
- **Test Runner**: Vitest (fast, Vite-native)
- **Testing Library**: React Testing Library (user-centric testing)
- **Mocking**: MSW (Mock Service Worker) for API mocking
- **E2E Testing**: Playwright for cross-browser testing
- **Coverage**: c8 for code coverage reporting

### Unit Testing

#### Component Testing
```tsx
// src/components/ChatInterface/ChatInterface.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ChatInterface } from './ChatInterface';
import { mockMessages } from '../../../__mocks__/data';

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
  beforeEach(() => {
    // Clear any previous test state
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render chat input placeholder', () => {
      renderWithProviders(<ChatInterface />);
      expect(screen.getByPlaceholderText('Ask Gemini')).toBeInTheDocument();
    });

    it('should render message history', () => {
      renderWithProviders(<ChatInterface messages={mockMessages} />);
      expect(screen.getByText('provide a summary analysis of the data')).toBeInTheDocument();
    });

    it('should display send and microphone buttons', () => {
      renderWithProviders(<ChatInterface />);
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /microphone/i })).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should update input value when typing', () => {
      renderWithProviders(<ChatInterface />);
      const input = screen.getByPlaceholderText('Ask Gemini') as HTMLInputElement;
      
      fireEvent.change(input, { target: { value: 'Test message' } });
      expect(input.value).toBe('Test message');
    });

    it('should send message on Enter key press', async () => {
      const mockOnSend = jest.fn();
      renderWithProviders(<ChatInterface onSendMessage={mockOnSend} />);
      
      const input = screen.getByPlaceholderText('Ask Gemini');
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
      
      await waitFor(() => {
        expect(mockOnSend).toHaveBeenCalledWith('Test message');
      });
    });

    it('should clear input after sending message', async () => {
      const mockOnSend = jest.fn();
      renderWithProviders(<ChatInterface onSendMessage={mockOnSend} />);
      
      const input = screen.getByPlaceholderText('Ask Gemini') as HTMLInputElement;
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send/i }));
      
      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });

    it('should not send empty messages', () => {
      const mockOnSend = jest.fn();
      renderWithProviders(<ChatInterface onSendMessage={mockOnSend} />);
      
      fireEvent.click(screen.getByRole('button', { name: /send/i }));
      expect(mockOnSend).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when send fails', async () => {
      const mockOnSend = jest.fn().mockRejectedValue(new Error('Send failed'));
      renderWithProviders(<ChatInterface onSendMessage={mockOnSend} />);
      
      const input = screen.getByPlaceholderText('Ask Gemini');
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.click(screen.getByRole('button', { name: /send/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/error sending message/i)).toBeInTheDocument();
      });
    });
  });
});
```

#### Hook Testing
```tsx
// src/hooks/useDataUpload.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { useDataUpload } from './useDataUpload';

describe('useDataUpload', () => {
  const mockFile = new File(['test content'], 'test.csv', { type: 'text/csv' });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useDataUpload());
    
    expect(result.current.files).toEqual([]);
    expect(result.current.isUploading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should add files when uploadFiles is called', async () => {
    const mockOnSuccess = jest.fn();
    const { result } = renderHook(() => useDataUpload({ onSuccess: mockOnSuccess }));
    
    await act(async () => {
      await result.current.uploadFiles([mockFile]);
    });
    
    expect(result.current.files).toHaveLength(1);
    expect(mockOnSuccess).toHaveBeenCalledWith([mockFile]);
  });

  it('should handle upload errors', async () => {
    const mockOnError = jest.fn();
    // Mock fetch to reject
    global.fetch = jest.fn().mockRejectedValue(new Error('Upload failed'));
    
    const { result } = renderHook(() => useDataUpload({ onError: mockOnError }));
    
    await act(async () => {
      await result.current.uploadFiles([mockFile]);
    });
    
    expect(result.current.error).toBe('Upload failed');
    expect(mockOnError).toHaveBeenCalledWith('Upload failed');
  });

  it('should remove files by index', () => {
    const { result } = renderHook(() => useDataUpload());
    
    act(() => {
      result.current.uploadFiles([mockFile, mockFile]);
    });
    
    act(() => {
      result.current.removeFile(0);
    });
    
    expect(result.current.files).toHaveLength(1);
  });
});
```

### Integration Testing

#### API Integration Tests
```tsx
// src/services/api.test.ts
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { QueryClient } from '@tanstack/react-query';
import { apiClient } from './api';

const server = setupServer(
  rest.post('/api/v1/files/upload', (req, res, ctx) => {
    return res(ctx.json({
      session_id: 'test-session-id',
      files: [{
        file_id: 'test-file-id',
        filename: 'test.csv',
        size: 1024,
        status: 'processed'
      }]
    }));
  }),

  rest.post('/api/v1/query/process', (req, res, ctx) => {
    return res(ctx.json({
      query_id: 'test-query-id',
      result: { data: [{ region: 'North', sales: 1000 }] },
      explanation: 'Sales data by region'
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('API Integration', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
  });

  describe('File Upload', () => {
    it('should upload files successfully', async () => {
      const file = new File(['test'], 'test.csv', { type: 'text/csv' });
      const result = await apiClient.uploadFiles([file]);
      
      expect(result.session_id).toBe('test-session-id');
      expect(result.files).toHaveLength(1);
      expect(result.files[0].filename).toBe('test.csv');
    });

    it('should handle upload errors', async () => {
      server.use(
        rest.post('/api/v1/files/upload', (req, res, ctx) => {
          return res(ctx.status(400), ctx.json({
            error: { message: 'File too large' }
          }));
        })
      );

      const file = new File(['test'], 'large.csv', { type: 'text/csv' });
      
      await expect(apiClient.uploadFiles([file])).rejects.toThrow('File too large');
    });
  });

  describe('Query Processing', () => {
    it('should process queries successfully', async () => {
      const result = await apiClient.processQuery({
        session_id: 'test-session-id',
        query: 'Show sales by region'
      });
      
      expect(result.query_id).toBe('test-query-id');
      expect(result.result.data).toEqual([{ region: 'North', sales: 1000 }]);
    });
  });
});
```

### E2E Testing with Playwright

#### Setup Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8080',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    }
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
  },
});
```

#### E2E Test Examples
```typescript
// e2e/data-analysis-workflow.spec.ts
import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Data Analysis Workflow', () => {
  test('should complete full analysis workflow', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Verify landing page
    await expect(page.locator('h1')).toContainText('Give me data and I will give you insights');
    
    // Upload a file
    const fileChooser = page.locator('input[type="file"]');
    await fileChooser.setInputFiles(path.join(__dirname, 'fixtures', 'sample-sales.csv'));
    
    // Wait for file processing
    await expect(page.locator('[data-testid="file-upload-success"]')).toBeVisible();
    await expect(page.locator('[data-testid="uploaded-file"]')).toContainText('sample-sales.csv');
    
    // Send a query
    const chatInput = page.locator('[placeholder="Ask Gemini"]');
    await chatInput.fill('Show me sales trends by region');
    await chatInput.press('Enter');
    
    // Verify AI response
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible();
    await expect(page.locator('[data-testid="results-table"]')).toBeVisible();
    
    // Verify data visualization
    await expect(page.locator('[data-testid="chart-container"]')).toBeVisible();
    
    // Test export functionality
    await page.locator('[data-testid="export-button"]').click();
    await page.locator('[data-testid="export-csv"]').click();
    
    // Verify download starts
    const downloadPromise = page.waitForEvent('download');
    await page.locator('[data-testid="confirm-export"]').click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/.*\.csv$/);
  });

  test('should handle file upload errors gracefully', async ({ page }) => {
    await page.goto('/');
    
    // Try to upload invalid file type
    const fileChooser = page.locator('input[type="file"]');
    await fileChooser.setInputFiles(path.join(__dirname, 'fixtures', 'invalid.txt'));
    
    // Verify error message
    await expect(page.locator('[data-testid="upload-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="upload-error"]')).toContainText('Unsupported file format');
  });

  test('should maintain conversation context', async ({ page }) => {
    await page.goto('/');
    
    // Upload file and ask initial question
    const fileChooser = page.locator('input[type="file"]');
    await fileChooser.setInputFiles(path.join(__dirname, 'fixtures', 'sample-sales.csv'));
    await expect(page.locator('[data-testid="file-upload-success"]')).toBeVisible();
    
    const chatInput = page.locator('[placeholder="Ask Gemini"]');
    await chatInput.fill('What is the total sales?');
    await chatInput.press('Enter');
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible();
    
    // Ask follow-up question
    await chatInput.fill('Which region had the highest sales?');
    await chatInput.press('Enter');
    
    // Verify contextual response
    await expect(page.locator('[data-testid="ai-response"]').last()).toBeVisible();
    await expect(page.locator('[data-testid="ai-response"]').last()).toContainText(/region/i);
  });
});
```

## Backend Testing Strategy

### Testing Stack
- **Test Framework**: pytest with async support
- **HTTP Testing**: FastAPI TestClient
- **Database Testing**: SQLAlchemy with SQLite for tests
- **Mocking**: pytest-mock and responses
- **Coverage**: pytest-cov for coverage reporting

### Unit Testing

#### Service Layer Tests
```python
# tests/unit/services/test_llm_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.llm_service import LLMService
from app.schemas.query import QueryRequest, QueryResult
from app.core.exceptions import LLMServiceError

class TestLLMService:
    @pytest.fixture
    def mock_anthropic_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def llm_service(self, mock_anthropic_client):
        service = LLMService()
        service.client = mock_anthropic_client
        return service
    
    @pytest.mark.asyncio
    async def test_process_query_success(self, llm_service, mock_anthropic_client):
        # Arrange
        query_request = QueryRequest(
            session_id="test-session",
            query="Show sales by region"
        )
        
        mock_anthropic_client.messages.create.return_value.content = [
            MagicMock(text='{"intent": "aggregate", "operation": "groupby", "column": "region"}')
        ]
        
        # Act
        result = await llm_service.process_query(query_request)
        
        # Assert
        assert result.intent == "aggregate"
        assert "region" in result.generated_code
        mock_anthropic_client.messages.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query_api_error(self, llm_service, mock_anthropic_client):
        # Arrange
        query_request = QueryRequest(
            session_id="test-session",
            query="Show sales by region"
        )
        
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")
        
        # Act & Assert
        with pytest.raises(LLMServiceError, match="API Error"):
            await llm_service.process_query(query_request)
    
    def test_classify_intent_sales_query(self, llm_service):
        # Test intent classification
        query = "Show me sales trends by quarter"
        intent = llm_service._classify_intent(query)
        assert intent == "aggregate"
    
    def test_extract_entities_from_query(self, llm_service):
        # Test entity extraction
        query = "Filter customers where age > 25 and region = 'North'"
        entities = llm_service._extract_entities(query)
        
        assert entities["table"] == "customers"
        assert len(entities["filters"]) == 2
        assert entities["filters"][0]["column"] == "age"
        assert entities["filters"][0]["operator"] == ">"
        assert entities["filters"][0]["value"] == 25
```

#### Data Processing Tests
```python
# tests/unit/services/test_data_service.py
import pytest
import pandas as pd
from io import BytesIO
from app.services.data_service import DataProcessingService
from app.core.exceptions import ValidationError, ProcessingError

class TestDataProcessingService:
    @pytest.fixture
    def data_service(self):
        return DataProcessingService()
    
    @pytest.fixture
    def sample_csv_content(self):
        csv_data = """region,sales,date
North,1000,2024-01-01
South,1500,2024-01-02
East,2000,2024-01-03"""
        return csv_data.encode('utf-8')
    
    @pytest.fixture
    def sample_excel_content(self):
        df = pd.DataFrame({
            'region': ['North', 'South', 'East'],
            'sales': [1000, 1500, 2000],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        return buffer.getvalue()
    
    def test_process_csv_file_success(self, data_service, sample_csv_content):
        # Act
        result = data_service.process_file(
            file_content=sample_csv_content,
            filename="sales.csv",
            user_id="test-user"
        )
        
        # Assert
        assert result["status"] == "success"
        assert len(result["data"]) == 3
        assert result["metadata"]["rows"] == 3
        assert result["metadata"]["columns"] == 3
        assert "region" in result["metadata"]["column_types"]
    
    def test_process_excel_file_success(self, data_service, sample_excel_content):
        # Act
        result = data_service.process_file(
            file_content=sample_excel_content,
            filename="sales.xlsx",
            user_id="test-user"
        )
        
        # Assert
        assert result["status"] == "success"
        assert len(result["data"]) == 3
    
    def test_process_unsupported_format(self, data_service):
        # Act & Assert
        with pytest.raises(ValidationError, match="Unsupported file format"):
            data_service.process_file(
                file_content=b"invalid content",
                filename="file.txt",
                user_id="test-user"
            )
    
    def test_process_corrupted_file(self, data_service):
        # Act & Assert
        with pytest.raises(ProcessingError):
            data_service.process_file(
                file_content=b"corrupted csv content",
                filename="corrupted.csv",
                user_id="test-user"
            )
    
    def test_infer_column_types(self, data_service):
        # Arrange
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'price': [10.5, 20.0, 15.75],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'active': [True, False, True]
        })
        
        # Act
        column_types = data_service._infer_column_types(df)
        
        # Assert
        assert column_types['id'] == 'integer'
        assert column_types['name'] == 'string'
        assert column_types['price'] == 'float'
        assert column_types['date'] == 'datetime'
        assert column_types['active'] == 'boolean'
```

### Integration Testing

#### API Endpoint Tests
```python
# tests/integration/test_query_endpoints.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.session import DataSession

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
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    return response.json()

@pytest.fixture
def auth_headers(client, test_user):
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_session(client, auth_headers):
    # Create a test session with uploaded file
    files = {"files": ("test.csv", "region,sales\nNorth,1000\nSouth,1500", "text/csv")}
    response = client.post("/api/v1/files/upload", files=files, headers=auth_headers)
    return response.json()["session_id"]

class TestQueryEndpoints:
    def test_process_query_success(self, client, auth_headers, test_session):
        # Arrange
        query_data = {
            "session_id": test_session,
            "query": "Show me sales by region"
        }
        
        # Act
        response = client.post(
            "/api/v1/query/process",
            json=query_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "query_id" in data
        assert "result" in data
        assert "explanation" in data
    
    def test_process_query_invalid_session(self, client, auth_headers):
        # Arrange
        query_data = {
            "session_id": "invalid-session-id",
            "query": "Show me data"
        }
        
        # Act
        response = client.post(
            "/api/v1/query/process",
            json=query_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
    
    def test_process_query_unauthorized(self, client, test_session):
        # Arrange
        query_data = {
            "session_id": test_session,
            "query": "Show me data"
        }
        
        # Act
        response = client.post("/api/v1/query/process", json=query_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_get_query_history(self, client, auth_headers, test_session):
        # Arrange - First create some queries
        for i in range(3):
            query_data = {
                "session_id": test_session,
                "query": f"Query {i}"
            }
            client.post("/api/v1/query/process", json=query_data, headers=auth_headers)
        
        # Act
        response = client.get(
            f"/api/v1/query/history/{test_session}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["queries"]) == 3
    
    def test_query_validation_error(self, client, auth_headers, test_session):
        # Arrange
        query_data = {
            "session_id": test_session,
            "query": ""  # Empty query
        }
        
        # Act
        response = client.post(
            "/api/v1/query/process",
            json=query_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 422
```

### Performance Testing

#### Load Testing
```python
# tests/performance/test_load.py
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import requests

class LoadTester:
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {auth_token}"}
    
    def test_query_endpoint_performance(self, concurrent_users: int = 10, requests_per_user: int = 5):
        """Test query endpoint under load."""
        
        def make_request():
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/query/process",
                json={
                    "session_id": "test-session",
                    "query": "Show sales by region"
                },
                headers=self.headers
            )
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            for _ in range(concurrent_users * requests_per_user):
                futures.append(executor.submit(make_request))
            
            results = [future.result() for future in futures]
        
        # Analyze results
        response_times = [r["response_time"] for r in results]
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        print(f"Success Rate: {success_rate:.2%}")
        print(f"Average Response Time: {statistics.mean(response_times):.3f}s")
        print(f"95th Percentile: {statistics.quantiles(response_times, n=20)[18]:.3f}s")
        print(f"Max Response Time: {max(response_times):.3f}s")
        
        # Assert performance requirements
        assert success_rate >= 0.95  # 95% success rate
        assert statistics.mean(response_times) < 3.0  # Average under 3 seconds
        assert statistics.quantiles(response_times, n=20)[18] < 5.0  # 95th percentile under 5 seconds

@pytest.mark.performance
def test_api_performance():
    # This would run against a staging environment
    tester = LoadTester("http://localhost:8000", "test-token")
    tester.test_query_endpoint_performance(concurrent_users=20, requests_per_user=10)
```

## Test Data Management

### Test Fixtures
```python
# tests/fixtures/data_fixtures.py
import pandas as pd
from pathlib import Path

class TestDataFixtures:
    @staticmethod
    def create_sample_sales_data() -> pd.DataFrame:
        """Create sample sales data for testing."""
        return pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100, freq='D'),
            'region': ['North', 'South', 'East', 'West'] * 25,
            'product': ['A', 'B', 'C'] * 33 + ['A'],
            'sales': range(1000, 1100),
            'profit': range(100, 200)
        })
    
    @staticmethod
    def create_customer_data() -> pd.DataFrame:
        """Create sample customer data for testing."""
        return pd.DataFrame({
            'customer_id': range(1, 51),
            'name': [f'Customer {i}' for i in range(1, 51)],
            'age': list(range(25, 75)),
            'region': ['North', 'South', 'East', 'West'] * 12 + ['North', 'South'],
            'total_purchases': range(100, 150)
        })
    
    @staticmethod
    def save_test_files(output_dir: Path):
        """Save test data files to disk."""
        output_dir.mkdir(exist_ok=True)
        
        # Save CSV files
        sales_data = TestDataFixtures.create_sample_sales_data()
        sales_data.to_csv(output_dir / 'sample-sales.csv', index=False)
        
        customer_data = TestDataFixtures.create_customer_data()
        customer_data.to_csv(output_dir / 'sample-customers.csv', index=False)
        
        # Save Excel file
        with pd.ExcelWriter(output_dir / 'sample-data.xlsx') as writer:
            sales_data.to_excel(writer, sheet_name='Sales', index=False)
            customer_data.to_excel(writer, sheet_name='Customers', index=False)
```

### Mock Data Services
```typescript
// src/__mocks__/api.ts
export const mockApiClient = {
  uploadFiles: jest.fn().mockResolvedValue({
    session_id: 'mock-session-id',
    files: [{
      file_id: 'mock-file-id',
      filename: 'mock-data.csv',
      size: 1024,
      status: 'processed',
      rows: 100,
      columns: 5
    }]
  }),

  processQuery: jest.fn().mockResolvedValue({
    query_id: 'mock-query-id',
    result: {
      data: [
        { region: 'North', sales: 1000 },
        { region: 'South', sales: 1500 },
        { region: 'East', sales: 2000 }
      ]
    },
    explanation: 'Sales data aggregated by region',
    execution_time: 0.5
  }),

  getQueryHistory: jest.fn().mockResolvedValue({
    queries: [
      {
        id: 'query-1',
        query: 'Show sales by region',
        created_at: '2024-01-01T10:00:00Z'
      }
    ]
  })
};
```

## Test Configuration

### Vitest Configuration
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    coverage: {
      provider: 'c8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

### Test Setup
```typescript
// src/test/setup.ts
import '@testing-library/jest-dom';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor(cb: any) {}
  observe() {}
  disconnect() {}
};

// Setup MSW server for API mocking
export const server = setupServer(
  rest.get('/api/health', (req, res, ctx) => {
    return res(ctx.json({ status: 'ok' }));
  })
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## CI/CD Integration

### GitHub Actions Test Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: data-insider-4/package-lock.json
    
    - name: Install dependencies
      working-directory: ./data-insider-4
      run: npm ci
    
    - name: Run type checking
      working-directory: ./data-insider-4
      run: npm run type-check
    
    - name: Run linting
      working-directory: ./data-insider-4
      run: npm run lint
    
    - name: Run unit tests
      working-directory: ./data-insider-4
      run: npm run test:coverage
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./data-insider-4/coverage/lcov.info
        flags: frontend

  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      working-directory: ./backend
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run code formatting check
      working-directory: ./backend
      run: black --check .
    
    - name: Run linting
      working-directory: ./backend
      run: ruff .
    
    - name: Run type checking
      working-directory: ./backend
      run: mypy .
    
    - name: Run tests
      working-directory: ./backend
      run: pytest --cov=app --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [frontend-tests, backend-tests]
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
    
    - name: Install dependencies
      working-directory: ./data-insider-4
      run: npm ci
    
    - name: Install Playwright browsers
      working-directory: ./data-insider-4
      run: npx playwright install --with-deps
    
    - name: Build application
      working-directory: ./data-insider-4
      run: npm run build
    
    - name: Run E2E tests
      working-directory: ./data-insider-4
      run: npx playwright test
    
    - name: Upload Playwright report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: data-insider-4/playwright-report/
        retention-days: 30
```

## Test Maintenance

### Regular Test Review
- **Weekly**: Review test failures and flaky tests
- **Monthly**: Analyze test coverage and identify gaps
- **Quarterly**: Update test data and scenarios
- **Release**: Full regression testing

### Test Quality Metrics
- **Coverage**: Minimum 80% code coverage
- **Performance**: Tests should run in under 5 minutes
- **Reliability**: Less than 1% flaky test rate
- **Maintainability**: Tests should be self-documenting

This comprehensive testing strategy ensures the Data Intelligence Platform maintains high quality, reliability, and performance while enabling rapid development and deployment cycles.