# Development Guide

## Prerequisites

### Required Software
- **Node.js**: v18.0.0 or higher ([install with nvm](https://github.com/nvm-sh/nvm))
- **Python**: 3.11 or higher
- **Docker**: Latest version for containerized development
- **Git**: Version control system
- **VS Code**: Recommended IDE with extensions (see below)

### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-json"
  ]
}
```

## Project Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd data-modeling-4

# Install frontend dependencies
cd data-insider-4
npm install

# Install backend dependencies (when backend is added)
cd ../backend
pip install -r requirements.txt
```

### 2. Environment Configuration

**Frontend Environment Variables** (`.env.local`):
```env
VITE_API_URL=http://localhost:8000
VITE_ANTHROPIC_API_KEY=your_api_key_here
VITE_MAX_FILE_SIZE=524288000
```

**Backend Environment Variables** (`.env`):
```env
# API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key  # Alternative LLM
API_VERSION=v1
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/data_intelligence
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
SESSION_TIMEOUT=86400  # 24 hours in seconds

# File Upload Limits
MAX_FILE_SIZE=524288000  # 500MB in bytes
MAX_FILES_PER_SESSION=20
SESSION_DATA_RETENTION=86400  # 24 hours

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

### 3. Database Setup (Future)

```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d postgres redis

# Run database migrations
cd backend
alembic upgrade head
```

## Development Workflow

### Frontend Development

**Start Development Server**:
```bash
cd data-insider-4
npm run dev
```
- Server: `http://localhost:8080`
- Hot reload enabled
- TypeScript compilation on save

**Available Scripts**:
```bash
npm run dev          # Start development server
npm run build        # Production build
npm run build:dev    # Development build with source maps
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Backend Development (Future Setup)

**Start Development Server**:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Auto-reload on file changes

**Available Scripts**:
```bash
python -m pytest                    # Run tests
python -m pytest --cov=app         # Run tests with coverage
black app/                          # Format code
ruff app/                           # Lint code
mypy app/                           # Type checking
alembic upgrade head                # Run migrations
```

## Development Standards

### Git Workflow

**Branch Naming Convention**:
```
feature/description-of-feature
bugfix/description-of-bug
hotfix/critical-fix
chore/maintenance-task
```

**Commit Message Format**:
```
type(scope): description

feat(chat): add message history persistence
fix(upload): resolve file validation error
docs(api): update endpoint documentation
refactor(data): simplify processing pipeline
test(upload): add file validation tests
```

**Pull Request Process**:
1. Create feature branch from `main`
2. Implement changes with tests
3. Run linting and type checking
4. Submit PR with clear description
5. Address review feedback
6. Merge after approval

### Code Review Guidelines

**What to Review**:
- Code functionality and logic
- Performance implications
- Security considerations
- Test coverage
- Documentation updates
- TypeScript type safety

**Review Checklist**:
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Documentation is updated
- [ ] Breaking changes are documented

## File Structure

### Frontend Structure
```
data-insider-4/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── ui/            # shadcn/ui components (auto-generated)
│   │   ├── Chat/          # Chat-related components
│   │   ├── DataUpload/    # File upload components  
│   │   ├── DataTable/     # Data display components
│   │   └── Layout/        # Layout components
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility functions
│   ├── pages/             # Route components
│   ├── services/          # API clients
│   ├── types/             # TypeScript definitions
│   └── utils/             # Helper functions
├── tests/                 # Test files
└── docs/                  # Component documentation
```

### Backend Structure (Planned)
```
backend/
├── app/
│   ├── api/               # API routes
│   │   ├── endpoints/     # Individual route files
│   │   └── dependencies/  # Dependency injection
│   ├── core/              # Core configuration
│   ├── db/                # Database models and utilities
│   ├── services/          # Business logic
│   │   ├── llm_service.py    # LLM integration
│   │   ├── data_service.py   # Data processing
│   │   └── auth_service.py   # Authentication
│   ├── schemas/           # Pydantic models
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── migrations/            # Database migrations
└── scripts/               # Deployment scripts
```

## Development Tasks

### Adding New Components

**Frontend Component**:
```bash
# Create component directory
mkdir src/components/NewComponent

# Create component files
touch src/components/NewComponent/index.tsx
touch src/components/NewComponent/NewComponent.tsx
touch src/components/NewComponent/NewComponent.test.tsx
```

**Component Template**:
```tsx
import React from 'react';
import { Card } from '@/components/ui/card';

interface NewComponentProps {
  // Define props here
}

export const NewComponent: React.FC<NewComponentProps> = ({ }) => {
  return (
    <Card>
      {/* Component content */}
    </Card>
  );
};

export default NewComponent;
```

### Adding API Endpoints (Future)

**Endpoint Template**:
```python
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.request import RequestSchema
from app.schemas.response import ResponseSchema
from app.services.service import Service

router = APIRouter(prefix="/api/v1", tags=["endpoint"])

@router.post("/endpoint", response_model=ResponseSchema)
async def create_endpoint(
    request: RequestSchema,
    service: Service = Depends(get_service)
) -> ResponseSchema:
    try:
        result = await service.process(request)
        return ResponseSchema(data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Database Migrations (Future)

**Create Migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

**Apply Migration**:
```bash
alembic upgrade head
```

### Adding Tests

**Frontend Test Template**:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { NewComponent } from './NewComponent';

describe('NewComponent', () => {
  it('renders correctly', () => {
    render(<NewComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    render(<NewComponent />);
    fireEvent.click(screen.getByRole('button'));
    // Add assertions
  });
});
```

**Backend Test Template**:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoint():
    response = client.post("/api/v1/endpoint", json={"key": "value"})
    assert response.status_code == 200
    assert response.json()["key"] == "expected_value"
```

## Common Development Tasks

### Updating shadcn/ui Components
```bash
# Add new shadcn/ui component
npx shadcn@latest add button

# Update existing components  
npx shadcn@latest add --overwrite button
```

### Managing Dependencies

**Frontend Dependencies**:
```bash
# Add production dependency
npm install package-name

# Add development dependency
npm install -D package-name

# Update dependencies
npm update

# Check for outdated packages
npm outdated
```

**Backend Dependencies**:
```bash
# Add dependency
pip install package-name
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

### Debugging

**Frontend Debugging**:
- Use React DevTools browser extension
- Console logging with structured data
- TypeScript compiler errors in terminal
- Network tab for API request debugging

**Backend Debugging** (Future):
- FastAPI interactive docs at `/docs`
- Python debugger with breakpoints
- Structured logging with correlation IDs
- Database query logging

### Performance Optimization

**Frontend Optimization**:
- Use React.memo for expensive components
- Implement code splitting with React.lazy
- Optimize bundle size with webpack-bundle-analyzer
- Use TanStack Query for efficient data fetching

**Backend Optimization** (Future):
- Profile Python code with cProfile
- Monitor database query performance
- Implement caching with Redis
- Use async/await for I/O operations

## Troubleshooting

### Common Issues

**Node.js Version Mismatch**:
```bash
# Use correct Node.js version
nvm use 18
nvm install 18
```

**Port Already in Use**:
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

**TypeScript Errors**:
```bash
# Clear TypeScript cache
npx tsc --build --clean

# Restart TypeScript server in VS Code
Ctrl/Cmd + Shift + P > "TypeScript: Restart TS Server"
```

**Package Installation Issues**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Getting Help

1. **Check Documentation**: Review relevant docs in `/docs`
2. **Search Issues**: Look for similar problems in repository issues
3. **Debug Logs**: Check browser console and terminal output
4. **Ask Team**: Reach out to team members for assistance
5. **Create Issue**: Document and report new bugs or questions

This guide provides the foundation for productive development on the Data Intelligence Platform. Keep it updated as the project evolves!