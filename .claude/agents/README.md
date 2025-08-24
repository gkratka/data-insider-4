# Claude Agents for Data Intelligence Platform

## Overview

This directory contains specialized Claude agents designed for different roles in the Data Intelligence Platform development squad. Each agent has deep expertise in their domain while maintaining awareness of the overall project goals and architecture.

## 🤖 Agent Selection Guide

### **When to Use Each Agent**

#### 🎨 **Frontend Development**
- **[Frontend Engineer](./frontend-engineer.md)** - React/TypeScript development, UI components, responsive design
- Use for: Component development, state management, UI/UX implementation, performance optimization

#### ⚙️ **Backend Development** 
- **[Backend Engineer](./backend-engineer.md)** - FastAPI, Python APIs, database design, server logic
- Use for: API endpoints, data processing, authentication, database operations

#### 🔄 **Full-Stack Development**
- **[Fullstack Engineer](./fullstack-engineer.md)** - End-to-end feature development, system integration
- Use for: Complete feature implementation, API-frontend integration, cross-stack debugging

#### 📊 **Data & Analytics**
- **[Data Scientist](./data-scientist.md)** - Statistical analysis, ML models, data processing
- Use for: Data analysis features, pandas operations, statistical modeling, insights generation

#### 🧠 **AI Integration**
- **[LLM Integration Specialist](./llm-integration-specialist.md)** - Claude API, NLP, query processing
- Use for: Natural language processing, Claude API integration, prompt engineering

#### 🚀 **Infrastructure & Deployment**
- **[DevOps Engineer](./devops-engineer.md)** - Docker, CI/CD, cloud deployment, monitoring
- Use for: Containerization, deployment pipelines, infrastructure setup, performance monitoring

#### 🔍 **Quality Assurance**
- **[Test Engineer](./test-engineer.md)** - Testing strategies, automation, quality metrics
- Use for: Unit/integration/E2E tests, test automation, coverage analysis

#### 🔒 **Security**
- **[Security Specialist](./security-specialist.md)** - Security best practices, compliance, vulnerability assessment
- Use for: Authentication systems, data privacy, security reviews, compliance implementation

#### 📝 **Documentation & Communication**
- **[Technical Writer](./technical-writer.md)** - API docs, user guides, technical specifications
- Use for: Documentation creation, API specifications, user guides, knowledge base

#### 👀 **Code Quality**
- **[Code Reviewer](./code-reviewer.md)** - Code quality assessment, architecture review, best practices
- Use for: Code reviews, architecture feedback, performance analysis, standards enforcement

#### 📋 **Project Coordination**
- **[Project Manager](./project-manager.md)** - Sprint planning, task breakdown, risk management
- Use for: Project planning, requirement analysis, team coordination, progress tracking

## 🎯 Agent Collaboration Workflows

### **Feature Development Workflow**
```
1. Project Manager → Define requirements and break down tasks
2. Fullstack Engineer → Design overall architecture and data flow
3. Frontend Engineer → Implement UI components and user interactions
4. Backend Engineer → Create API endpoints and business logic
5. Data Scientist → Implement data processing and analysis features
6. LLM Specialist → Integrate natural language processing capabilities
7. Test Engineer → Create comprehensive test suite
8. Security Specialist → Review for security vulnerabilities
9. Code Reviewer → Final code quality assessment
10. DevOps Engineer → Deploy and monitor in production
11. Technical Writer → Update documentation
```

### **Bug Fix Workflow**
```
1. Code Reviewer → Analyze issue and identify root cause
2. Relevant specialist → Implement fix (Frontend/Backend/Data/etc.)
3. Test Engineer → Create regression tests and verify fix
4. Security Specialist → Ensure fix doesn't introduce vulnerabilities
5. DevOps Engineer → Deploy fix to production
```

### **Architecture Review Workflow**
```
1. Fullstack Engineer → Present architectural proposal
2. Backend Engineer → Review server-side implications
3. Frontend Engineer → Review client-side implications
4. Data Scientist → Review data processing impacts
5. Security Specialist → Review security implications
6. DevOps Engineer → Review deployment and scalability concerns
7. Project Manager → Assess timeline and resource implications
```

## 🔧 Project Context

All agents are pre-configured with knowledge of:

### **Current Project Phase**
- MVP Phase 1 - Foundation Development
- Focus on core file upload, chat interface, and basic data analysis

### **Technology Stack**
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python, pandas, NumPy, scikit-learn
- **AI**: Anthropic Claude API
- **Infrastructure**: Docker, PostgreSQL, Redis

### **Key Features**
- Natural language data queries
- Multi-file processing (CSV, Excel, JSON, Parquet)
- Interactive chat interface
- Statistical analysis and ML capabilities
- Real-time data processing

### **Documentation References**
Each agent has access to:
- [Product Requirements Document](/docs/prd.md)
- [Technical Architecture](/docs/technical-architecture.md)
- [Development Guide](/docs/development-guide.md)
- [API Documentation](/docs/api-documentation.md)
- [Coding Standards](/docs/coding-standards.md)
- [Testing Strategy](/docs/testing-strategy.md)
- [Deployment Guide](/docs/deployment-guide.md)

## 📈 Best Practices

### **Agent Selection**
- Choose the most specialized agent for your specific task
- Use Fullstack Engineer for cross-cutting concerns
- Consult multiple agents for complex architectural decisions

### **Collaboration**
- Reference other agents' suggestions when relevant
- Maintain consistency across all implementations
- Follow established coding standards and patterns

### **Context Sharing**
- Provide relevant background when switching between agents
- Reference previous decisions and architectural choices
- Maintain awareness of current development phase and priorities

## 🚀 Getting Started

1. **Identify your task type** using the selection guide above
2. **Choose the appropriate agent** based on your needs
3. **Provide context** about current work and requirements
4. **Follow up with related agents** if cross-domain expertise is needed
5. **Ensure consistency** with project standards and architecture

## 💡 Pro Tips

- **Multi-agent consultation**: For complex features, consult multiple agents in sequence
- **Context preservation**: When switching agents, provide summary of previous discussions
- **Documentation first**: Use Technical Writer agent to document new patterns and decisions
- **Review everything**: Always run final implementations through Code Reviewer agent
- **Security by design**: Include Security Specialist early in feature planning

---

**Last Updated**: January 2025  
**Agents Version**: 1.0  
**Project Phase**: MVP Phase 1