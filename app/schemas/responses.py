"""
Pydantic schemas for API responses and system definitions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import StockTrading, StockHistorical, StockMetrics, AlpacaStocks


class StocksListResponse(BaseModel):
    """Response for list of stocks"""
    count: int = Field(..., description="Number of stocks returned")
    limit: int = Field(..., description="Maximum number of results per page")
    offset: int = Field(..., description="Offset for pagination")
    stocks: List[StockTrading] = Field(..., description="List of stock trading data")

class AlpacaStocksListResponse(BaseModel):
    """Response for list of stocks"""
    count: int = Field(..., description="Number of stocks returned")
    limit: int = Field(..., description="Maximum number of results per page")
    offset: int = Field(..., description="Offset for pagination")
    stocks: List[AlpacaStocks] = Field(..., description="List of Alpaca stock trading data")


class LatestStocksResponse(BaseModel):
    """Response for latest stocks snapshot"""
    timestamp: Optional[datetime] = Field(None, description="Data snapshot timestamp")
    count: int = Field(..., description="Number of stocks returned")
    stocks: List[StockTrading] = Field(..., description="List of stock trading data")


class StockDetailResponse(BaseModel):
    """Response for single stock detail"""
    name: str = Field(..., description="Stock name/ticker")
    days: int = Field(..., description="Number of days of data")
    count: int = Field(..., description="Number of data points")
    data: List[StockTrading] = Field(..., description="Historical trading data")


class StockHistoricalResponse(BaseModel):
    """Response for stock historical data"""
    name: str = Field(..., description="Stock name/ticker")
    days: int = Field(..., description="Number of days of data")
    count: int = Field(..., description="Number of data points")
    data: List[StockHistorical] = Field(..., description="Historical comparison data")


class StockMetricsResponse(BaseModel):
    """Response for stock metrics"""
    name: str = Field(..., description="Stock name/ticker")
    days: int = Field(..., description="Number of days of data")
    count: int = Field(..., description="Number of data points")
    data: List[StockMetrics] = Field(..., description="Financial metrics data")


class SearchResponse(BaseModel):
    """Response for stock search"""
    query: str = Field(..., description="Search query")
    count: int = Field(..., description="Number of results")
    results: List[str] = Field(..., description="List of matching stock names")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "ABB",
                "count": 2,
                "results": ["ABB", "ABB Ltd"]
            }
        }


class DatabaseStats(BaseModel):
    """Database statistics"""
    total_stocks: int = Field(..., description="Total number of unique stocks")
    total_records: int = Field(..., description="Total number of data records")
    first_date: Optional[datetime] = Field(None, description="Earliest data timestamp")
    last_date: Optional[datetime] = Field(None, description="Latest data timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_stocks": 160,
                "total_records": 2080,
                "first_date": "2026-01-15T09:00:00",
                "last_date": "2026-01-16T15:30:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database connection status")
    db_type: str = Field(..., description="Database type")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "db_type": "postgresql"
            }
        }


class APIRoot(BaseModel):
    """API root response"""
    message: str = Field(..., description="API welcome message")
    version: str = Field(..., description="API version")
    endpoints: dict = Field(..., description="Available endpoints")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Stockster API",
                "version": "1.0.0",
                "endpoints": {
                    "stocks": "/stocks",
                    "stock": "/stocks/{name}",
                    "latest": "/stocks/latest",
                    "historical": "/stocks/{name}/historical",
                    "metrics": "/stocks/{name}/metrics",
                    "health": "/health"
                }
            }
        }