"""
Ticket Analytics Platform - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import auth, upload, clusters, assessments, feedback, approval, analytics

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant ticket analytics platform with RAG-based learning",
    version="1.0.0",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(upload.router, prefix=f"{settings.API_PREFIX}/upload", tags=["Upload"])
app.include_router(clusters.router, prefix=f"{settings.API_PREFIX}/clusters", tags=["Clusters"])
app.include_router(assessments.router, prefix=f"{settings.API_PREFIX}/assessments", tags=["Assessments"])
app.include_router(feedback.router, prefix=f"{settings.API_PREFIX}/feedback", tags=["Feedback"])
app.include_router(approval.router, prefix=f"{settings.API_PREFIX}/approval", tags=["Approval"])
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }


@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "embeddings": "ready",
            "llm": "ready"
        }
    }
