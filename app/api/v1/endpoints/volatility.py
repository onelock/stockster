"""
Volatility analysis API endpoints - fully dependency injection driven.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from ....core.dependencies import get_volatility_service
from ....services.volatility_service import VolatilityService

router = APIRouter(prefix="/volatility", tags=["volatility"])


@router.get("/{name}", response_model=Dict[str, Any])
async def get_stock_volatility(
    name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for volatility calculation"),
    service: VolatilityService = Depends(get_volatility_service)
) -> Dict[str, Any]:
    """
    Calculate volatility metrics for a specific stock.
    
    Returns average change, standard deviation, and min/max changes.
    
    - **name**: Stock name/ticker
    - **days**: Number of days to analyze (1-365)
    """
    result = service.calculate_volatility(name, days)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Insufficient data to calculate volatility for '{name}'"
        )
    return result


@router.get("/", response_model=Dict[str, Any])
async def get_most_volatile_stocks(
    days: int = Query(30, ge=1, le=365, description="Number of days for volatility calculation"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    service: VolatilityService = Depends(get_volatility_service)
) -> Dict[str, Any]:
    """
    Get most volatile stocks ranked by standard deviation.
    
    - **days**: Number of days to analyze (1-365)
    - **limit**: Maximum number of stocks to return (1-50)
    """
    stocks = service.get_most_volatile(days, limit)
    return {
        "days": days,
        "limit": limit,
        "count": len(stocks),
        "stocks": stocks
    }