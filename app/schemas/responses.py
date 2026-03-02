"""
Pydantic schemas for API responses and system definitions.
"""

from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from .models import StockTrading, StockHistorical, StockMetrics, AlpacaStocks


class StockTradingResponse(SQLModel):
    """Base trading data for a stock"""
    name: str = Field(index=True, max_length=50, description="Stock name/ticker")
    last_price: Optional[Decimal] = Field(None, description="Last traded price", max_digits=12, decimal_places=2)
    change_abs: Optional[Decimal] = Field(None, description="Absolute price change", max_digits=12, decimal_places=2)
    change_pct: Optional[Decimal] = Field(None, description="Percentage price change", max_digits=8, decimal_places=2)
    highest: Optional[Decimal] = Field(None, description="Highest price of the day", max_digits=12, decimal_places=2)
    lowest: Optional[Decimal] = Field(None, description="Lowest price of the day", max_digits=12, decimal_places=2)
    volume: Optional[int] = Field(None, description="Trading volume")
    market_value: Optional[int] = Field(None, description="Market capitalization")
    list: Optional[str] = Field(None, max_length=100, description="Market Capital list of stock")
    timestamp: datetime = Field(index=True, description="Data timestamp")
    href: Optional[str] = Field(None, description="URL to stock details")

class StocksListResponse(SQLModel):
    """Response for list of stocks"""
    count: int = Field(..., description="Number of stocks returned")
    limit: int = Field(..., description="Maximum number of results per page")
    offset: int = Field(..., description="Offset for pagination")
    data: List[StockTrading] = Field(..., description="List of stock trading data")

class AlpacaStocksListResponse(SQLModel):
    """Response for list of stocks"""
    count: int = Field(..., description="Number of stocks returned")
    limit: int = Field(..., description="Maximum number of results per page")
    offset: int = Field(..., description="Offset for pagination")
    data: List[AlpacaStocks] = Field(..., description="List of Alpaca stock trading data")


class LatestStocksResponse(SQLModel):
    """Response for latest stocks snapshot"""
    timestamp: Optional[datetime] = Field(None, description="Data snapshot timestamp")
    count: int = Field(..., description="Number of stocks returned")
    data: List[StockTrading] = Field(..., description="List of stock trading data")


class StockDetailResponse(SQLModel):
    """Response for single stock detail"""
    name: str = Field(..., description="Stock name/ticker")
    days: int = Field(..., description="Number of days of data")
    count: int = Field(..., description="Number of data points")
    data: List[StockTrading] = Field(..., description="Historical trading data")


class StockHistoricalResponse(SQLModel):
    """Response for stock historical data"""
    name: str = Field(..., description="Stock name/ticker")
    days: int = Field(..., description="Number of days of data")
    count: int = Field(..., description="Number of data points")
    data: List[StockHistorical] = Field(..., description="Historical comparison data")


class StockMetricsResponse(SQLModel):
    """Response for stock metrics"""
    name: str = Field(..., description="Stock name/ticker")
    days: int = Field(..., description="Number of days of data")
    count: int = Field(..., description="Number of data points")
    data: List[StockMetrics] = Field(..., description="Financial metrics data")


class SearchResponse(SQLModel):
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


class DatabaseStats(SQLModel):
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


class HealthResponse(SQLModel):
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


class APIRoot(SQLModel):
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