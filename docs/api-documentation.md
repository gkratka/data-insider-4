# API Documentation

## Overview

The Data Intelligence Platform API is built with FastAPI, providing a modern REST API with automatic OpenAPI documentation, request/response validation, and async processing capabilities.

**Base URL**: `http://localhost:8000/api/v1` (development)  
**Interactive Docs**: `http://localhost:8000/docs`  
**OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Authentication

### JWT Token Authentication
```http
Authorization: Bearer <jwt_token>
```

**Obtain Token**:
```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Session Management
Sessions are managed server-side with Redis, automatically created upon first file upload.

## Core API Endpoints

### File Upload Endpoints

#### Upload Files
Upload one or more data files for analysis.

```http
POST /api/v1/files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

files: File[]  # One or more files
session_id?: string  # Optional existing session
```

**Supported Formats**: CSV, Excel (.xlsx, .xls), JSON, Parquet  
**File Size Limit**: 500MB per file, 2GB total per session

**Response**:
```json
{
  "session_id": "uuid-session-id",
  "files": [
    {
      "file_id": "uuid-file-id",
      "filename": "sales_data.csv",
      "size": 1048576,
      "format": "csv",
      "rows": 10000,
      "columns": 8,
      "status": "processed",
      "schema": {
        "columns": [
          {"name": "date", "type": "datetime"},
          {"name": "region", "type": "string"},
          {"name": "sales", "type": "float"}
        ]
      },
      "preview": [
        {"date": "2024-01-01", "region": "North", "sales": 1000.0},
        // ... first 10 rows
      ]
    }
  ],
  "total_files": 1,
  "total_size": 1048576
}
```

#### List Uploaded Files
Retrieve information about files in a session.

```http
GET /api/v1/files/{session_id}
Authorization: Bearer <token>
```

**Response**:
```json
{
  "session_id": "uuid-session-id",
  "files": [/* file objects */],
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2024-01-02T00:00:00Z"
}
```

#### Delete File
Remove a file from the session.

```http
DELETE /api/v1/files/{session_id}/{file_id}
Authorization: Bearer <token>
```

### Query Processing Endpoints

#### Process Natural Language Query
Convert natural language queries into data operations and execute them.

```http
POST /api/v1/query/process
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "uuid-session-id",
  "query": "Show me sales trends by region for Q4 2024",
  "context": {
    "previous_queries": ["uuid-query-1", "uuid-query-2"],
    "focus_tables": ["sales_data.csv"]
  }
}
```

**Response**:
```json
{
  "query_id": "uuid-query-id",
  "intent": "aggregate",
  "entities": {
    "tables": ["sales_data"],
    "columns": ["region", "sales", "date"],
    "filters": [{"column": "date", "operator": ">=", "value": "2024-10-01"}],
    "aggregations": [{"function": "sum", "column": "sales"}],
    "groupby": ["region"]
  },
  "generated_code": "df.groupby('region')['sales'].sum()",
  "result": {
    "type": "dataframe",
    "data": [
      {"region": "North", "sales": 150000},
      {"region": "South", "sales": 120000},
      {"region": "East", "sales": 180000},
      {"region": "West", "sales": 95000}
    ],
    "summary": "Sales by region for Q4 2024: East leads with $180K, followed by North ($150K), South ($120K), and West ($95K).",
    "insights": [
      "East region outperforms others by 20%",
      "West region shows opportunity for growth"
    ]
  },
  "execution_time": 0.85,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Get Query History
Retrieve previous queries and results for a session.

```http
GET /api/v1/query/history/{session_id}
Authorization: Bearer <token>
```

**Query Parameters**:
- `limit`: Number of queries to return (default: 50)
- `offset`: Pagination offset (default: 0)

### Data Export Endpoints

#### Export Query Results
Export query results in various formats.

```http
POST /api/v1/export/results
Authorization: Bearer <token>
Content-Type: application/json

{
  "query_id": "uuid-query-id",
  "format": "csv",  // csv, excel, json
  "filename": "sales_analysis_results"
}
```

**Response**:
```json
{
  "download_url": "/api/v1/export/download/uuid-export-id",
  "filename": "sales_analysis_results.csv",
  "size": 2048,
  "expires_at": "2024-01-01T01:00:00Z"
}
```

#### Download Exported File
```http
GET /api/v1/export/download/{export_id}
Authorization: Bearer <token>
```

Returns the file as an attachment with appropriate headers.

### Statistical Analysis Endpoints

#### Generate Statistical Summary
Create comprehensive statistical analysis for datasets.

```http
POST /api/v1/analysis/statistics
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "uuid-session-id",
  "file_ids": ["uuid-file-1", "uuid-file-2"],
  "analysis_type": "descriptive",  // descriptive, correlation, distribution
  "columns": ["sales", "profit", "quantity"]  // optional column filter
}
```

**Response**:
```json
{
  "analysis_id": "uuid-analysis-id",
  "type": "descriptive",
  "results": {
    "sales": {
      "count": 10000,
      "mean": 1250.5,
      "std": 425.2,
      "min": 100.0,
      "max": 5000.0,
      "percentiles": {"25": 950.0, "50": 1200.0, "75": 1500.0}
    },
    "profit": {
      /* similar structure */
    }
  },
  "correlations": {
    "sales_profit": 0.87,
    "sales_quantity": 0.65
  },
  "insights": [
    "Strong positive correlation between sales and profit",
    "Sales data shows normal distribution"
  ]
}
```

#### Build Predictive Model
Create and train machine learning models on uploaded data.

```http
POST /api/v1/analysis/model
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "uuid-session-id",
  "file_id": "uuid-file-id",
  "model_type": "regression",  // regression, classification, clustering
  "target_column": "sales",
  "feature_columns": ["region", "product", "season"],
  "model_params": {
    "algorithm": "random_forest",
    "test_size": 0.2,
    "cross_validation": true
  }
}
```

**Response**:
```json
{
  "model_id": "uuid-model-id",
  "type": "regression",
  "algorithm": "random_forest",
  "performance": {
    "r2_score": 0.85,
    "mse": 125.4,
    "mae": 8.9,
    "cv_scores": [0.83, 0.87, 0.84, 0.86, 0.85]
  },
  "feature_importance": [
    {"feature": "region", "importance": 0.45},
    {"feature": "product", "importance": 0.35},
    {"feature": "season", "importance": 0.20}
  ],
  "predictions": [
    {"actual": 1200, "predicted": 1185, "residual": 15},
    // ... test set predictions
  ],
  "model_summary": "Random Forest model achieves 85% accuracy predicting sales based on region, product, and season."
}
```

## WebSocket Endpoints

### Real-time Chat Connection
For real-time conversation updates and streaming responses.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/{session_id}?token={jwt_token}');

// Send message
ws.send(JSON.stringify({
  type: 'query',
  content: 'Analyze customer trends'
}));

// Receive streaming response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Message Types**:
- `query`: User question/request
- `response`: AI response chunk
- `result`: Final query results
- `error`: Error notifications
- `status`: Processing status updates

## Error Handling

### HTTP Status Codes
- `200`: Success
- `201`: Created successfully
- `400`: Bad request (validation error)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Resource not found
- `413`: File too large
- `422`: Validation error
- `429`: Rate limit exceeded
- `500`: Internal server error

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "File format not supported",
    "details": {
      "field": "file_type",
      "supported_formats": ["csv", "xlsx", "json", "parquet"]
    },
    "request_id": "uuid-request-id"
  }
}
```

### Common Error Codes
- `INVALID_FILE_FORMAT`: Unsupported file type
- `FILE_TOO_LARGE`: Exceeds size limits
- `SESSION_EXPIRED`: Session no longer valid
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `LLM_SERVICE_ERROR`: AI service unavailable
- `DATA_PROCESSING_ERROR`: Error in data analysis
- `INSUFFICIENT_DATA`: Not enough data for operation

## Rate Limiting

### Limits
- **File Uploads**: 20 files per hour per user
- **Queries**: 100 queries per hour per user
- **Exports**: 50 exports per hour per user
- **WebSocket**: 1 connection per session

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## SDK Examples

### Python Client Example
```python
import requests
from typing import List, Dict, Any

class DataIntelligenceClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def upload_files(self, files: List[str]) -> Dict[str, Any]:
        files_data = [('files', open(f, 'rb')) for f in files]
        response = requests.post(
            f"{self.base_url}/files/upload",
            files=files_data,
            headers=self.headers
        )
        return response.json()
    
    def query(self, session_id: str, question: str) -> Dict[str, Any]:
        payload = {
            "session_id": session_id,
            "query": question
        }
        response = requests.post(
            f"{self.base_url}/query/process",
            json=payload,
            headers=self.headers
        )
        return response.json()

# Usage
client = DataIntelligenceClient("http://localhost:8000/api/v1", "your-token")
upload_result = client.upload_files(["sales.csv", "customers.xlsx"])
query_result = client.query(upload_result["session_id"], "Show me top customers by revenue")
```

### JavaScript Client Example
```javascript
class DataIntelligenceAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async uploadFiles(files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await fetch(`${this.baseUrl}/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });
    
    return await response.json();
  }

  async processQuery(sessionId, query) {
    const response = await fetch(`${this.baseUrl}/query/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({
        session_id: sessionId,
        query: query
      })
    });
    
    return await response.json();
  }
}

// Usage
const api = new DataIntelligenceAPI('http://localhost:8000/api/v1', 'your-token');
const uploadResult = await api.uploadFiles([file1, file2]);
const queryResult = await api.processQuery(uploadResult.session_id, 'Analyze trends');
```

## Versioning

The API follows semantic versioning:
- **v1**: Current stable version
- **v2**: Future version with breaking changes

Version is specified in the URL path: `/api/v1/...`

## Testing

### Test Endpoints
Development environment includes test endpoints:

```http
GET /api/v1/health
# Health check endpoint

POST /api/v1/test/sample-data
# Generate sample datasets for testing
```

This API documentation will be updated as new endpoints and features are implemented.