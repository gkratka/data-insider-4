from fastapi import APIRouter
from app.api.endpoints import files, sessions, data, query, chat, statistics

# Main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])  
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(statistics.router, tags=["statistics"])