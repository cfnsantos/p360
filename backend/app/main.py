from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.api import api_router
from app.core.config import settings
from app.db.database import engine
from app.models import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="P360 Health & Wellness Platform",
    description="AI-powered health and wellness platform with ChatGPT integration",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve static files for frontend
if settings.ENVIRONMENT == "production":
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return {
        "message": "P360 Health & Wellness Platform API",
        "version": "1.0.0",
        "features": [
            "AI-powered chat interface",
            "Health recommendations",
            "Content generation",
            "Code assistance"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "P360 Backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True if settings.DEBUG else False
    )
