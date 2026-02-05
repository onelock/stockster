"""
Pydantic response schemas for Alpaca API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from .alpaca_models import AlpacaBar, AlpacaOHLCAggregated, AlpacaVolumeData


class AlpacaSymbolsListResponse(BaseModel):
    """Response for list of Alpaca symbols"""
    count: int = Field(..., description="Number of symbols returned")
    limit: int = Field(..., description="Maximum number of results per page")
    offset: int = Field(..., description="Offset for pagination")
    symbols: List[str] = Field(..., description="List of stock symbols")


class AlpacaBarsResponse(BaseModel):
    """Response for bar data"""
    symbol: str = Field(..., description="Stock symbol/ticker")
    days: int = Field(..., description="Number of days of data")
    count: int = Field(..., description="Number of data points")
    bars: List[AlpacaBar] = Field(..., description="OHLCV bar data")


class AlpacaLatestBarsResponse(BaseModel):
    """Response for latest bars of all symbols"""
    count: int = Field(..., description="Number of symbols")
    bars: List[AlpacaBar] = Field(..., description="Latest bar data for all symbols")


class AlpacaOHLCResponse(BaseModel):
    """Response for aggregated OHLC data"""
    symbol: str = Field(..., description="Stock symbol/ticker")
    days: int = Field(..., description="Number of days analyzed")
    data: AlpacaOHLCAggregated = Field(..., description="Aggregated OHLC statistics")


class AlpacaTopVolumeResponse(BaseModel):
    """Response for top volume symbols"""
    days: int = Field(..., description="Number of days analyzed")
    count: int = Field(..., description="Number of symbols returned")
    symbols: List[AlpacaVolumeData] = Field(..., description="Symbols ranked by volume")


class AlpacaSearchResponse(BaseModel):
    """Response for symbol search"""
    query: str = Field(..., description="Search query")
    count: int = Field(..., description="Number of results")
    symbols: List[str] = Field(..., description="List of matching symbols")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "AAP",
                "count": 2,
                "symbols": ["AAPL", "AAP"]
            }
        }

class AlpacaDatabaseStats(BaseModel):
    """Alpaca database statistics"""
    total_symbols: int = Field(..., description="Total number of unique symbols")
    total_records: int = Field(..., description="Total number of data records")
    first_date: Optional[str] = Field(None, description="Earliest data timestamp")
    last_date: Optional[str] = Field(None, description="Latest data timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_symbols": 50,
                "total_records": 64273,
                "first_date": "2025-12-01T09:30:00",
                "last_date": "2026-01-22T16:00:00"
            }
        }
