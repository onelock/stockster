"""
Stock-related API endpoints - fully dependency injection driven.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from ....core.dependencies import get_stock_service
from ....services.stock_service import StockService
from ....schemas import (
    StocksListResponse, LatestStocksResponse,
    StockDetailResponse, StockHistoricalResponse,
    StockMetricsResponse, SearchResponse, DatabaseStats,
    BulkInsertRequest
)

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/", response_model=StocksListResponse)
async def get_stocks(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: StockService = Depends(get_stock_service)
) -> StocksListResponse:
    """
    Get all stocks with pagination.
    
    - **limit**: Maximum number of stocks to return (1-1000)
    - **offset**: Number of stocks to skip for pagination
    """
    return service.get_stocks_list(limit, offset)


@router.get("/latest", response_model=LatestStocksResponse)
async def get_latest_stocks(
    service: StockService = Depends(get_stock_service)
) -> LatestStocksResponse:
    """
    Get the latest snapshot of all stocks.
    
    Returns the most recent data point for all stocks in the database.
    """
    return service.get_latest_stocks()


@router.get("/search", response_model=SearchResponse)
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query"),
    service: StockService = Depends(get_stock_service)
) -> SearchResponse:
    """
    Search for stocks by name.
    
    - **q**: Search query string (case-insensitive partial match)
    """
    return service.search_stocks(q)


@router.get("/stats", response_model=DatabaseStats)
async def get_stats(
    service: StockService = Depends(get_stock_service)
) -> DatabaseStats:
    """
    Get database statistics.
    
    Returns information about total stocks, records, and date ranges.
    """
    return service.get_stats()


@router.get("/{name}", response_model=StockDetailResponse)
async def get_stock(
    name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of historical data"),
    service: StockService = Depends(get_stock_service)
) -> StockDetailResponse:
    """
    Get detailed data for a specific stock.
    
    - **name**: Stock name/ticker
    - **days**: Number of days of historical data to retrieve (1-365)
    """
    result = service.get_stock_detail(name, days)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Stock '{name}' not found or no data available"
        )
    return result


@router.get("/{name}/historical", response_model=StockHistoricalResponse)
async def get_stock_historical(
    name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of historical data"),
    service: StockService = Depends(get_stock_service)
) -> StockHistoricalResponse:
    """
    Get historical comparison data for a stock.
    
    Includes year-high, period returns, etc.
    
    - **name**: Stock name/ticker
    - **days**: Number of days of historical data to retrieve (1-365)
    """
    result = service.get_stock_historical(name, days)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Historical data for '{name}' not found"
        )
    return result


@router.get("/{name}/metrics", response_model=StockMetricsResponse)
async def get_stock_metrics(
    name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of metrics data"),
    service: StockService = Depends(get_stock_service)
) -> StockMetricsResponse:
    """
    Get financial metrics for a stock.
    
    Includes P/E ratio, dividend yield, earnings per share, etc.
    
    - **name**: Stock name/ticker
    - **days**: Number of days of metrics data to retrieve (1-365)
    """
    result = service.get_stock_metrics(name, days)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"Metrics for '{name}' not found"
        )
    return result


@router.post("/bulk", response_model=dict)
async def bulk_insert_stocks(
    data: BulkInsertRequest,
    service: StockService = Depends(get_stock_service)
) -> dict:
    """
    Bulk insert stock data from scraper.
    
    Accepts trading, historical, and metrics data in bulk.
    Use this endpoint to populate the database from scrapers.
    """
    try:
        # Convert Pydantic models to dicts
        trading_data = [item.model_dump() for item in data.trading]
        historical_data = [item.model_dump() for item in data.historical]
        metrics_data = [item.model_dump() for item in data.metrics]
        
        result = service.bulk_insert_data(
            trading_data, 
            historical_data, 
            metrics_data
        )
        
        return {
            "success": True,
            "message": "Data inserted successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to insert data: {str(e)}"
        )