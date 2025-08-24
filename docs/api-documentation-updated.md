# Data Intelligence Platform - Complete API Documentation

## 📋 Overview

The Data Intelligence Platform API provides programmatic access to data upload, processing, and analysis capabilities. This RESTful API enables developers to integrate data intelligence features into their applications.

**Base URL**: `https://api.dataintelligence.com/v1`  
**Authentication**: JWT Bearer tokens  
**Rate Limits**: 1000 requests/hour (authenticated), 100 requests/hour (unauthenticated)

## 🔐 Authentication

### Obtain Access Token

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using Tokens

Include the token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 👤 User Management

### Create User Account

```http
POST /users/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-01-15T10:30:00Z",
  "is_active": true
}
```

### Get User Profile

```http
GET /users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-15T14:22:00Z",
  "storage_used": 1024000,
  "storage_limit": 5368709120
}
```

## 📁 File Management

### Upload File

```http
POST /files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@data.csv
```

**Response:**
```json
{
  "id": "file_123e4567-e89b-12d3-a456-426614174000",
  "filename": "data.csv",
  "original_filename": "sales_data.csv",
  "file_type": "csv",
  "file_size": 1024000,
  "upload_date": "2025-01-15T10:30:00Z",
  "status": "processed",
  "row_count": 1500,
  "column_count": 8,
  "columns": ["id", "date", "product", "quantity", "price", "customer", "region", "total"],
  "preview_url": "/files/file_123e4567/preview"
}
```

### List Files

```http
GET /files?limit=10&offset=0&sort_by=upload_date&order=desc
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit`: Number of results per page (max 100)
- `offset`: Number of results to skip
- `sort_by`: Sort field (upload_date, filename, file_size)
- `order`: Sort order (asc, desc)
- `file_type`: Filter by file type (csv, xlsx, json, parquet)

**Response:**
```json
{
  "files": [
    {
      "id": "file_123e4567-e89b-12d3-a456-426614174000",
      "filename": "data.csv",
      "file_type": "csv",
      "file_size": 1024000,
      "upload_date": "2025-01-15T10:30:00Z",
      "status": "processed",
      "row_count": 1500,
      "column_count": 8
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

### Get File Details

```http
GET /files/{file_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "file_123e4567-e89b-12d3-a456-426614174000",
  "filename": "data.csv",
  "original_filename": "sales_data.csv",
  "file_type": "csv",
  "file_size": 1024000,
  "upload_date": "2025-01-15T10:30:00Z",
  "status": "processed",
  "row_count": 1500,
  "column_count": 8,
  "columns": ["id", "date", "product", "quantity", "price", "customer", "region", "total"],
  "data_types": {
    "id": "integer",
    "date": "datetime",
    "product": "string",
    "quantity": "integer",
    "price": "float",
    "customer": "string",
    "region": "string",
    "total": "float"
  },
  "summary_stats": {
    "total_records": 1500,
    "missing_values": 12,
    "duplicate_records": 3
  }
}
```

### File Preview

```http
GET /files/{file_id}/preview?limit=100
Authorization: Bearer <token>
```

**Response:**
```json
{
  "headers": ["id", "date", "product", "quantity", "price", "customer", "region", "total"],
  "rows": [
    ["1", "2025-01-01", "Widget A", "5", "29.99", "John Doe", "West", "149.95"],
    ["2", "2025-01-01", "Widget B", "2", "39.99", "Jane Smith", "East", "79.98"]
  ],
  "total_rows": 1500,
  "preview_rows": 100
}
```

### Delete File

```http
DELETE /files/{file_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "File deleted successfully",
  "deleted_at": "2025-01-15T15:30:00Z"
}
```

## 📊 Data Processing

### Query Data

```http
POST /data/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "query": {
    "operation": "filter",
    "conditions": [
      {
        "column": "region",
        "operator": "eq",
        "value": "West"
      },
      {
        "column": "quantity",
        "operator": "gt",
        "value": 3
      }
    ]
  }
}
```

**Response:**
```json
{
  "query_id": "query_987fcdeb-51a2-4b3c-d456-426614174000",
  "result": {
    "headers": ["id", "date", "product", "quantity", "price", "customer", "region", "total"],
    "rows": [
      ["1", "2025-01-01", "Widget A", "5", "29.99", "John Doe", "West", "149.95"],
      ["15", "2025-01-02", "Widget C", "4", "19.99", "Bob Wilson", "West", "79.96"]
    ],
    "row_count": 2,
    "execution_time": 0.045
  }
}
```

### Aggregate Data

```http
POST /data/aggregate
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "group_by": ["region"],
  "aggregations": {
    "total_sales": {"column": "total", "function": "sum"},
    "avg_quantity": {"column": "quantity", "function": "mean"},
    "order_count": {"column": "id", "function": "count"}
  }
}
```

**Response:**
```json
{
  "result": {
    "headers": ["region", "total_sales", "avg_quantity", "order_count"],
    "rows": [
      ["West", "15420.75", "3.2", "245"],
      ["East", "18950.30", "2.8", "312"],
      ["North", "12750.00", "4.1", "185"],
      ["South", "16200.45", "3.5", "201"]
    ],
    "execution_time": 0.125
  }
}
```

### Sort Data

```http
POST /data/sort
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "sort_columns": [
    {"column": "total", "direction": "desc"},
    {"column": "date", "direction": "asc"}
  ],
  "limit": 50
}
```

## 🤖 AI Chat Interface

### Start Chat Session

```http
POST /chat/sessions/new
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_id": "session_456e7890-1234-5678-9abc-def012345678",
  "created_at": "2025-01-15T10:30:00Z",
  "expires_at": "2025-01-15T18:30:00Z"
}
```

### Send Message

```http
POST /chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "session_456e7890-1234-5678-9abc-def012345678",
  "message": "Show me the top 5 products by sales revenue",
  "file_context": ["file_123e4567-e89b-12d3-a456-426614174000"]
}
```

**Response:**
```json
{
  "message_id": "msg_789abcde-f012-3456-7890-123456789abc",
  "response": {
    "content": "Here are the top 5 products by sales revenue from your data:",
    "data": {
      "headers": ["product", "total_revenue"],
      "rows": [
        ["Widget A", "4250.75"],
        ["Widget B", "3890.50"],
        ["Widget C", "3120.25"],
        ["Widget D", "2950.00"],
        ["Widget E", "2780.30"]
      ]
    },
    "visualization": {
      "type": "bar_chart",
      "chart_url": "/charts/chart_123abc/image"
    }
  },
  "timestamp": "2025-01-15T10:35:00Z",
  "processing_time": 2.3
}
```

### Get Chat History

```http
GET /chat/history/{session_id}?limit=50
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_id": "session_456e7890-1234-5678-9abc-def012345678",
  "messages": [
    {
      "id": "msg_123",
      "role": "user",
      "content": "Show me the top 5 products by sales revenue",
      "timestamp": "2025-01-15T10:35:00Z"
    },
    {
      "id": "msg_124",
      "role": "assistant",
      "content": "Here are the top 5 products by sales revenue from your data:",
      "data": {...},
      "timestamp": "2025-01-15T10:35:02Z"
    }
  ]
}
```

## 📈 Statistics & Analytics

### Descriptive Statistics

```http
POST /statistics/descriptive
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "columns": ["quantity", "price", "total"]
}
```

**Response:**
```json
{
  "statistics": {
    "quantity": {
      "count": 1500,
      "mean": 3.2,
      "std": 1.8,
      "min": 1,
      "25%": 2,
      "50%": 3,
      "75%": 4,
      "max": 10
    },
    "price": {
      "count": 1500,
      "mean": 29.45,
      "std": 12.30,
      "min": 9.99,
      "25%": 19.99,
      "50%": 29.99,
      "75%": 39.99,
      "max": 99.99
    }
  }
}
```

### Correlation Analysis

```http
POST /statistics/correlation
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "columns": ["quantity", "price", "total"],
  "method": "pearson"
}
```

**Response:**
```json
{
  "correlation_matrix": {
    "quantity": {"quantity": 1.0, "price": 0.1, "total": 0.85},
    "price": {"quantity": 0.1, "price": 1.0, "total": 0.75},
    "total": {"quantity": 0.85, "price": 0.75, "total": 1.0}
  },
  "method": "pearson"
}
```

### Regression Analysis

```http
POST /statistics/regression
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "target_column": "total",
  "feature_columns": ["quantity", "price"],
  "model_type": "linear"
}
```

**Response:**
```json
{
  "model_type": "linear_regression",
  "r_squared": 0.892,
  "coefficients": {
    "quantity": 28.45,
    "price": 2.15,
    "intercept": -12.30
  },
  "p_values": {
    "quantity": 0.001,
    "price": 0.003
  },
  "predictions_url": "/statistics/regression/predict/model_123abc"
}
```

## 🎨 Visualizations

### Create Chart

```http
POST /visualizations/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "chart_type": "bar",
  "x_column": "product",
  "y_column": "total",
  "aggregation": "sum",
  "title": "Sales by Product",
  "color_scheme": "viridis"
}
```

**Response:**
```json
{
  "chart_id": "chart_123abc-def4-5678-90gh-ijklmnopqrst",
  "chart_url": "/visualizations/chart_123abc",
  "image_url": "/visualizations/chart_123abc/image.png",
  "interactive_url": "/visualizations/chart_123abc/interactive",
  "created_at": "2025-01-15T10:40:00Z"
}
```

### Get Chart

```http
GET /visualizations/{chart_id}
Authorization: Bearer <token>
```

### Export Chart

```http
GET /visualizations/{chart_id}/export?format=png&width=800&height=600
Authorization: Bearer <token>
```

**Formats**: png, svg, pdf, html

## 💾 Data Export

### Export Data

```http
POST /export/data
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567-e89b-12d3-a456-426614174000",
  "format": "xlsx",
  "include_metadata": true,
  "filters": {
    "region": "West"
  }
}
```

**Response:**
```json
{
  "export_id": "export_789xyz-abc1-2345-6789-def012345678",
  "download_url": "/export/download/export_789xyz",
  "expires_at": "2025-01-16T10:30:00Z",
  "file_size": 245760,
  "format": "xlsx"
}
```

### Export Analysis Results

```http
POST /export/analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "session_456e7890-1234-5678-9abc-def012345678",
  "include_charts": true,
  "include_data": true,
  "format": "pdf",
  "template": "executive_summary"
}
```

## 📊 System Monitoring

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "file_storage": "healthy",
    "ai_service": "healthy"
  },
  "uptime": 86400
}
```

### API Metrics

```http
GET /metrics
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "requests_per_minute": 45.2,
  "average_response_time": 285,
  "error_rate": 0.02,
  "active_users": 123,
  "storage_used": 5368709120,
  "ai_queries_today": 1847
}
```

## 🔧 Advanced Queries

### Multi-table Join

```http
POST /data/join
Authorization: Bearer <token>
Content-Type: application/json

{
  "left_file_id": "file_123e4567",
  "right_file_id": "file_789abcde",
  "join_type": "inner",
  "left_on": "customer_id",
  "right_on": "id",
  "columns": ["customer_name", "order_date", "product", "total"]
}
```

### Time Series Analysis

```http
POST /analytics/timeseries
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567",
  "date_column": "order_date",
  "value_column": "total",
  "frequency": "monthly",
  "analysis_type": "trend"
}
```

### Machine Learning

```http
POST /ml/predict
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "file_123e4567",
  "target_column": "churn",
  "feature_columns": ["age", "tenure", "monthly_spend"],
  "model_type": "random_forest",
  "test_size": 0.2
}
```

## ❌ Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File size exceeds limit |
| 415 | Unsupported Media Type | File format not supported |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | System maintenance or overload |

## 📞 Support & Resources

- **API Status**: https://status.dataintelligence.com
- **Documentation**: https://docs.dataintelligence.com
- **Support Email**: api-support@dataintelligence.com
- **Developer Forum**: https://forum.dataintelligence.com
- **SDK Libraries**: Available for Python, JavaScript, R, and Java

---

**API Version**: v1.0  
**Documentation Updated**: January 2025  
**Rate Limits**: Subject to change with notice