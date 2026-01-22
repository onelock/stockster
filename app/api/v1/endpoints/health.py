"""
Health check and system endpoints - fully dependency injection driven.
"""
from fastapi import APIRouter, Depends
from ....core.database import get_db
from ....core.config import settings
from ....schemas import HealthResponse, APIRoot

router = APIRouter(tags=["system"])


@router.get("/", response_model=APIRoot)
async def root() -> APIRoot:
    """
    API root endpoint.
    
    Returns API information and available endpoints.
    """
    return APIRoot(
        message=settings.app_name,
        version=settings.app_version,
        endpoints={
            "stocks": f"{settings.api_v1_prefix}/stocks",
            "stock_detail": f"{settings.api_v1_prefix}/stocks/{{name}}",
            "latest": f"{settings.api_v1_prefix}/stocks/latest",
            "historical": f"{settings.api_v1_prefix}/stocks/{{name}}/historical",
            "metrics": f"{settings.api_v1_prefix}/stocks/{{name}}/metrics",
            "search": f"{settings.api_v1_prefix}/stocks/search",
            "stats": f"{settings.api_v1_prefix}/stocks/stats",
            "volatility": f"{settings.api_v1_prefix}/volatility/{{name}}",
            "most_volatile": f"{settings.api_v1_prefix}/volatility",
            "health": f"{settings.api_v1_prefix}/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    )


@router.get("/health", response_model=HealthResponse)
async def health_check(conn=Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint.
    
    Verifies database connectivity and returns service status.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return HealthResponse(
            status="healthy",
            database="connected",
            db_type="postgresql"
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            database=f"error: {str(e)}",
            db_type="postgresql"
        )