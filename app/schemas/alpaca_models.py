"""
Pydantic models for Alpaca stock data.
"""
from pydantic import BaseModel, Field
from typing import Optional

class AlpacaBar(BaseModel):
    """OHLCV bar data from Alpaca"""
    symbol: str = Field(..., description="Stock symbol/ticker")
    timestamp: str = Field(..., description="Bar timestamp")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="Highest price")
    low: Optional[float] = Field(None, description="Lowest price")
    close: Optional[float] = Field(None, description="Closing price")
    volume: Optional[float] = Field(None, description="Trading volume")
    trade_count: Optional[int] = Field(None, description="Number of trades")
    vwap: Optional[float] = Field(None, description="Volume weighted average price")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "timestamp": "2026-01-16T09:30:00",
                "open": 150.25,
                "high": 152.50,
                "low": 149.80,
                "close": 151.75,
                "volume": 1250000,
                "trade_count": 4567,
                "vwap": 151.20
            }
        }


class AlpacaOHLCAggregated(BaseModel):
    """Aggregated OHLC data for a symbol"""
    symbol: str = Field(..., description="Stock symbol/ticker")
    min_open: Optional[float] = Field(None, description="Minimum opening price")
    max_high: Optional[float] = Field(None, description="Maximum high price")
    min_low: Optional[float] = Field(None, description="Minimum low price")
    avg_close: Optional[float] = Field(None, description="Average closing price")
    total_volume: Optional[float] = Field(None, description="Total volume")
    total_trades: Optional[int] = Field(None, description="Total trade count")
    avg_vwap: Optional[float] = Field(None, description="Average VWAP")
    data_points: int = Field(..., description="Number of data points")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "min_open": 148.50,
                "max_high": 155.20,
                "min_low": 147.80,
                "avg_close": 151.35,
                "total_volume": 50000000,
                "total_trades": 125000,
                "avg_vwap": 151.10,
                "data_points": 30
            }
        }


class AlpacaVolumeData(BaseModel):
    """Trading volume statistics for a symbol"""
    symbol: str = Field(..., description="Stock symbol/ticker")
    total_volume: Optional[float] = Field(None, description="Total volume")
    total_trades: Optional[int] = Field(None, description="Total trade count")
    avg_vwap: Optional[float] = Field(None, description="Average VWAP")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "total_volume": 50000000,
                "total_trades": 125000,
                "avg_vwap": 151.10
            }
        }
