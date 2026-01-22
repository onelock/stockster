"""
Alpaca stock data API endpoints - fully dependency injection driven.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional
from ....core.dependencies import get_alpaca_service
from ....services.alpaca_service import AlpacaService
from ....schemas import (
    AlpacaSymbolsListResponse,
    AlpacaBarsResponse,
    AlpacaLatestBarsResponse,
    AlpacaBar,
    AlpacaOHLCResponse,
    AlpacaTopVolumeResponse,
    AlpacaSearchResponse,
    AlpacaDatabaseStats
)

router = APIRouter(prefix="/alpaca", tags=["alpaca"])


@router.get("/symbols", response_model=AlpacaSymbolsListResponse)
async def get_symbols(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaSymbolsListResponse:
    """
    Get all available stock symbols with pagination.
    
    - **limit**: Maximum number of symbols to return (1-1000)
    - **offset**: Number of symbols to skip for pagination
    """
    return service.get_symbols_list(limit, offset)


@router.get("/symbols/search", response_model=AlpacaSearchResponse)
async def search_symbols(
    q: str = Query(..., min_length=1, description="Search query"),
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaSearchResponse:
    """
    Search for symbols by partial match.
    
    - **q**: Search query string (case-insensitive partial match)
    """
    return service.search_symbols(q)


@router.get("/bars/latest", response_model=AlpacaLatestBarsResponse)
async def get_latest_bars(
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaLatestBarsResponse:
    """
    Get the latest bar data for all symbols.
    
    Returns the most recent OHLCV data point for all available symbols.
    """
    return service.get_latest_all_symbols()


@router.get("/bars/{symbol}", response_model=AlpacaBarsResponse)
async def get_symbol_bars(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of historical data"),
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaBarsResponse:
    """
    Get historical bar data for a specific symbol.
    
    - **symbol**: Stock symbol/ticker (e.g., AAPL, GOOGL)
    - **days**: Number of days of historical data to retrieve (1-365)
    """
    result = service.get_symbol_bars(symbol.upper(), days)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for symbol '{symbol}'"
        )
    return result


@router.get("/bars/{symbol}/latest", response_model=AlpacaBar)
async def get_symbol_latest_bar(
    symbol: str,
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaBar:
    """
    Get the most recent bar data for a specific symbol.
    
    - **symbol**: Stock symbol/ticker (e.g., AAPL, GOOGL)
    """
    result = service.get_latest_bar(symbol.upper())
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for symbol '{symbol}'"
        )
    return result


@router.get("/bars/{symbol}/range", response_model=AlpacaBarsResponse)
async def get_symbol_bars_range(
    symbol: str,
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaBarsResponse:
    """
    Get bar data for a symbol within a specific date range.
    
    - **symbol**: Stock symbol/ticker (e.g., AAPL, GOOGL)
    - **start_date**: Start date in ISO format (e.g., 2026-01-01T00:00:00)
    - **end_date**: End date in ISO format (e.g., 2026-01-31T23:59:59)
    """
    result = service.get_bars_by_date_range(symbol.upper(), start_date, end_date)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for symbol '{symbol}' in the specified date range"
        )
    return result


@router.get("/ohlc/{symbol}", response_model=AlpacaOHLCResponse)
async def get_symbol_ohlc(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to aggregate"),
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaOHLCResponse:
    """
    Get aggregated OHLC statistics for a symbol.
    
    Returns min/max/avg statistics across the specified time period.
    
    - **symbol**: Stock symbol/ticker (e.g., AAPL, GOOGL)
    - **days**: Number of days to analyze (1-365)
    """
    result = service.get_ohlc_aggregated(symbol.upper(), days)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for symbol '{symbol}'"
        )
    return result


@router.get("/volume/top", response_model=AlpacaTopVolumeResponse)
async def get_top_volume(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaTopVolumeResponse:
    """
    Get symbols with highest trading volume.
    
    Returns top symbols ranked by total trading volume over the specified period.
    
    - **days**: Number of days to analyze (1-30)
    - **limit**: Maximum number of symbols to return (1-50)
    """
    return service.get_top_volume_symbols(days, limit)


@router.get("/stats", response_model=AlpacaDatabaseStats)
async def get_stats(
    service: AlpacaService = Depends(get_alpaca_service)
) -> AlpacaDatabaseStats:
    """
    Get database statistics for Alpaca data.
    
    Returns information about total symbols, records, and date ranges.
    """
    return service.get_stats()
