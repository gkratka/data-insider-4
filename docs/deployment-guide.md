# Deployment Guide

## Overview

The Data Intelligence Platform is designed for cloud-native deployment with containerization support. This guide covers deployment strategies for development, staging, and production environments.

## Deployment Architecture

### Development Environment
- **Local Development**: Docker Compose for full stack
- **Frontend Only**: Vite dev server with API mocking
- **Database**: Local PostgreSQL and Redis containers

### Staging Environment
- **Platform**: AWS ECS or Google Cloud Run
- **Database**: Managed PostgreSQL (RDS/Cloud SQL)
- **Cache**: Managed Redis (ElastiCache/Memory Store)
- **Storage**: S3/Cloud Storage for file uploads

### Production Environment
- **Platform**: Kubernetes or managed container service
- **High Availability**: Multi-zone deployment
- **Auto-scaling**: CPU/memory-based scaling
- **Monitoring**: Full observability stack

## Prerequisites

### Required Accounts & Services
- **Cloud Provider**: AWS, Google Cloud, or Azure
- **Container Registry**: Docker Hub, ECR, or GCR
- **Domain**: Custom domain with SSL certificate
- **Monitoring**: DataDog, New Relic, or similar
- **LLM API**: Anthropic Claude API key

### Required Tools
- **Docker**: Container runtime
- **Docker Compose**: Local orchestration
- **Kubernetes CLI**: For K8s deployments
- **Cloud CLI**: AWS CLI, gcloud, or az
- **Terraform**: Infrastructure as Code (optional)

## Docker Configuration

### Frontend Dockerfile
```dockerfile
# data-insider-4/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./data-insider-4
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/data_intelligence
      - REDIS_URL=redis://redis:6379/0
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./backend:/app
      - /app/__pycache__

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=data_intelligence
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Cloud Deployment

### AWS Deployment

#### ECS with Fargate
```yaml
# aws-ecs-task-definition.json
{
  "family": "data-intelligence-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/data-intelligence-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/data-intelligence",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "frontend"
        }
      }
    },
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/data-intelligence-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/db"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:anthropic-api-key"
        }
      ]
    }
  ]
}
```

### Google Cloud Deployment

#### Cloud Run Configuration
```yaml
# gcp-cloudrun-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: data-intelligence-backend
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 80
      containers:
      - image: gcr.io/project-id/data-intelligence-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-url
              key: url
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: anthropic-api-key
              key: key
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
```

## Kubernetes Deployment

### Backend Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: data-intelligence
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/data-intelligence-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: DATABASE_URL
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-key
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: data-intelligence
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

## Environment Configuration

### Production Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://user:pass@db-host:5432/data_intelligence
REDIS_URL=redis://redis-host:6379/0
ANTHROPIC_API_KEY=your-anthropic-api-key
JWT_SECRET_KEY=your-super-secret-jwt-key
CORS_ORIGINS=["https://yourdomain.com"]
ENVIRONMENT=production
LOG_LEVEL=INFO

# File Upload
MAX_FILE_SIZE=524288000
UPLOAD_STORAGE_PATH=/tmp/uploads
S3_BUCKET_NAME=data-intelligence-uploads
S3_REGION=us-west-2

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST=20

# Monitoring
DATADOG_API_KEY=your-datadog-key
SENTRY_DSN=your-sentry-dsn
```

### Secrets Management

**Kubernetes Secrets**:
```bash
# Create secrets
kubectl create secret generic api-secrets \
  --from-literal=anthropic-key="your-api-key" \
  --from-literal=jwt-secret="your-jwt-secret" \
  --namespace=data-intelligence

kubectl create secret generic db-secrets \
  --from-literal=database-url="postgresql://user:pass@host:5432/db" \
  --namespace=data-intelligence
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Data Intelligence Platform

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME_FRONTEND: data-intelligence-frontend
  IMAGE_NAME_BACKEND: data-intelligence-backend

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: data-insider-4/package-lock.json
    
    - name: Install frontend dependencies
      working-directory: ./data-insider-4
      run: npm ci
    
    - name: Run frontend tests
      working-directory: ./data-insider-4
      run: |
        npm run lint
        npm run build

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./data-insider-4
        push: true
        tags: ${{ env.REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME_FRONTEND }}:latest
```

## Monitoring and Health Checks

### Health Check Endpoint
```python
# backend/app/api/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
import redis

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Database check
    try:
        db.execute("SELECT 1")
        checks["checks"]["database"] = "healthy"
    except Exception as e:
        checks["checks"]["database"] = f"unhealthy: {str(e)}"
        checks["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["checks"]["redis"] = "healthy"
    except Exception as e:
        checks["checks"]["redis"] = f"unhealthy: {str(e)}"
        checks["status"] = "unhealthy"
    
    return checks
```

## Security Configuration

### HTTPS and SSL
```nginx
# nginx.conf for frontend
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # File upload size
    client_max_body_size 500M;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

## Backup and Disaster Recovery

### Database Backup Script
```bash
#!/bin/bash
# backup-database.sh

DATESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups/postgresql"
DATABASE_NAME="data_intelligence"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATESTAMP.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$DATESTAMP.sql.gz s3://your-backup-bucket/database/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

### Automated Backup Schedule
```yaml
# k8s/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: data-intelligence
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump $DATABASE_URL | gzip > /backup/backup_$(date +%Y%m%d_%H%M%S).sql.gz
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secrets
                  key: database-url
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

This deployment guide provides comprehensive instructions for deploying the Data Intelligence Platform across different environments and cloud providers. Adapt the configurations based on your specific requirements and infrastructure preferences.