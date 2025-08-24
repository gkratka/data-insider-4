# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Data Intelligence Platform - a web-based application that democratizes data analysis by combining conversational LLM capabilities with Python data science tools. Users upload data files and perform complex operations through natural language queries.

**Key Goal**: Transform plain English queries into data operations, making advanced analytics accessible to both technical and non-technical users.

## Development Commands

**Start Development Server**
```bash
cd data-insider-4
npm run dev
```
Server runs on http://localhost:8080

**Build Commands**
```bash
npm run build          # Production build
npm run build:dev      # Development build
npm run preview        # Preview production build
```

**Code Quality**
```bash
npm run lint           # ESLint validation
```

**Install Dependencies**
```bash
npm install            # Install all dependencies
```

## Architecture Overview

### Current State (Frontend Only - Phase 1 Foundation)
- **Framework**: React 18 + TypeScript + Vite
- **UI**: Tailwind CSS + shadcn/ui components (Radix primitives)  
- **State**: No global state management yet (prepare for Zustand/Redux Toolkit)
- **Routing**: React Router DOM with basic routes
- **Dev Tools**: ESLint, TypeScript strict mode disabled for rapid prototyping

### Target Architecture (Per PRD)
- **Frontend**: React + TypeScript + shadcn/ui + TanStack Query
- **Backend**: FastAPI (Python) with pandas/scikit-learn
- **LLM**: Anthropic Claude API integration
- **Data Processing**: Pandas, NumPy for operations; temporary Redis storage
- **Deployment**: Docker containers

## Key Components

**Core UI Components** (`src/components/`)
- `UploadSection.tsx` - File upload interface with drag-and-drop (not functional yet)
- `UploadedFiles.tsx` - Display uploaded files and metadata  
- `ChatInterface.tsx` - Conversation UI with message history (has sample data)

**Component Architecture**
- All UI components built with shadcn/ui (consistent design system)
- TypeScript interfaces defined for data structures
- Responsive design with Tailwind CSS
- Icons via Lucide React

## File Structure
```
data-insider-4/
├── src/
│   ├── components/           # React components
│   │   ├── ui/              # shadcn/ui components (do not modify directly)
│   │   ├── ChatInterface.tsx
│   │   ├── UploadSection.tsx 
│   │   └── UploadedFiles.tsx
│   ├── pages/               # Route components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   └── main.tsx            # App entry point
├── package.json
└── vite.config.ts
```

## Implementation Priorities (Per PRD Phase 1)

1. **File Upload System** - Implement drag-and-drop with validation (CSV, Excel support)
2. **Backend API** - Create FastAPI server with upload endpoints  
3. **LLM Integration** - Connect to Anthropic Claude API
4. **Data Processing** - Pandas operations for basic queries
5. **Results Display** - Enhanced data table with export functionality
6. **Session Management** - Maintain uploaded tables in memory/Redis

## Development Guidelines

### Component Standards
- Use TypeScript interfaces for all props and data structures
- Follow existing shadcn/ui patterns for consistency
- Implement responsive design (mobile-first)
- Use proper error boundaries and loading states

### API Integration Planning  
- Prepare for TanStack Query integration (already installed)
- Structure for future WebSocket support (real-time chat)
- Design for session-based data persistence

### File Upload Implementation
- Support: CSV, Excel (.xlsx, .xls), JSON, Parquet formats
- File size limits: 500MB per file, 2GB per session
- Automatic encoding detection and data preview
- Integrate with react-dropzone (needs to be added)

### LLM Integration Strategy
- Intent classification for data operations (filter, aggregate, join, model)
- Entity extraction for table/column references  
- Query disambiguation with clarifying questions
- Python code generation for pandas operations

## Environment Setup

**Required Environment Variables** (for future backend):
```env
ANTHROPIC_API_KEY=your_api_key
MAX_FILE_SIZE=524288000
SESSION_TIMEOUT=86400
```

**Dependencies to Add**:
- `react-dropzone` - File upload handling
- `@tanstack/react-table` - Advanced data tables
- Backend: `fastapi`, `pandas`, `anthropic` Python packages

## Current Limitations & Next Steps

**Current State**: Static frontend with sample data
**Immediate Needs**:
1. Functional file upload with validation
2. Backend API development (FastAPI)  
3. LLM integration for query processing
4. Data processing engine with pandas
5. Real-time chat functionality

**Technical Debt**:
- TypeScript strict mode disabled (noImplicitAny: false)
- No error handling or loading states yet
- Sample data hardcoded in ChatInterface
- No actual data processing capabilities

## PRD Reference

Full product requirements in `/docs/prd.md` - reference for:
- User personas and workflows
- Functional requirements and success metrics  
- Technical architecture decisions
- MVP scope and feature prioritization
- Non-functional requirements (performance, security)

This codebase is currently a foundation for the full Data Intelligence Platform vision.