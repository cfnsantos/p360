from fastapi import APIRouter

from app.api.endpoints import chat, health, content, code_assistance

api_router = APIRouter()

# Include all API endpoint routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(code_assistance.router, prefix="/code", tags=["code-assistance"])
