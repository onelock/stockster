"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import settings
from .core.database import close_db_connections
from .api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    print("🚀 Starting Stockster API...")
    print("📊 Using SQLModel/SQLAlchemy for database operations")
    yield
    # Shutdown
    print("🛑 Shutting down Stockster API...")
    close_db_connections()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Stock market data API with PostgreSQL backend",
    version=settings.app_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )