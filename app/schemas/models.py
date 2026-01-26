"""
Core Pydantic data models for stock data entities.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StockTrading(BaseModel):
    """Trading data for a stock"""
    name: str = Field(..., description="Stock name/ticker")
    last_price: Optional[float] = Field(None, description="Last traded price")
    change_abs: Optional[float] = Field(None, description="Absolute price change")
    change_pct: Optional[float] = Field(None, description="Percentage price change")
    highest: Optional[float] = Field(None, description="Highest price of the day")
    lowest: Optional[float] = Field(None, description="Lowest price of the day")
    volume: Optional[int] = Field(None, description="Trading volume")
    market_value: Optional[int] = Field(None, description="Market capitalization")
    list: Optional[str] = Field(None, description="Market Capital list of stock ")
    timestamp: datetime = Field(..., description="Data timestamp")
    href: Optional[str] = Field(None, description="URL to stock details")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ABB",
                "last_price": 705.8,
                "change_abs": -2.4,
                "change_pct": -0.34,
                "highest": 710.4,
                "lowest": 704.6,
                "volume": 181972,
                "market_value": 1301793,
                "list": "Large Cap",
                "timestamp": "2026-01-16T14:15:21",
                "href": "/bors/aktier/abb-730/"
            }
        }


class StockHistorical(BaseModel):
    """Historical comparison data for a stock"""
    name: str = Field(..., description="Stock name/ticker")
    year_high: Optional[float] = Field(None, description="52-week high price")
    date_year_high: Optional[float] = Field(None, description="Date of 52-week high")
    period_1d: Optional[float] = Field(None, description="1-day change %")
    period_1m: Optional[float] = Field(None, description="1-month change %")
    period_ytd: Optional[float] = Field(None, description="Year-to-date change %")
    period_1y: Optional[float] = Field(None, description="1-year change %")
    list: Optional[str] = Field(None, description="Market Capital list of stock ")
    timestamp: datetime = Field(..., description="Data timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ABB",
                "year_high": 697.0,
                "date_year_high": 726.4,
                "period_1d": -0.34,
                "period_1m": 3.61,
                "period_ytd": 2.05,
                "period_1y": 2.62,
                "list": "Large Cap",
                "timestamp": "2026-01-16T14:15:21"
            }
        }


class StockMetrics(BaseModel):
    """Key financial metrics for a stock"""
    name: str = Field(..., description="Stock name/ticker")
    pe_ratio: Optional[float] = Field(None, description="Price-to-Earnings ratio")
    ps_ratio: Optional[float] = Field(None, description="Price-to-Sales ratio")
    earning_per_share: Optional[float] = Field(None, description="Earnings per share")
    equity_per_share: Optional[float] = Field(None, description="Equity per share")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield %")
    direct_return: Optional[float] = Field(None, description="Direct return %")
    list: Optional[str] = Field(None, description="Market Capital list of stock ")
    timestamp: datetime = Field(..., description="Data timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ABB",
                "pe_ratio": 30.0,
                "ps_ratio": 3.58,
                "earning_per_share": 23.6,
                "equity_per_share": 90.32,
                "dividend_yield": 10.94,
                "direct_return": 2.8,
                "list": "Large Cap",
                "timestamp": "2026-01-16T14:15:21"
            }
        }
        
class AlpacaStocks(BaseModel):
    """Key financial metrics for a stock"""
    symbol: str = Field(..., description="Stock name/ticker")
    timestamp: datetime = Field(..., description="Data timestamp")
    open: Optional[float] = Field(None, description="Opening stock price")
    high: Optional[float] = Field(None, description="Highest stock price")
    low: Optional[float] = Field(None, description="Lowest stock price")
    close: Optional[float] = Field(None, description="Closing stock price")
    volume: Optional[float] = Field(None, description="Total number of shares")
    trade_count: Optional[float] = Field(None, description="Total number of trades")
    vwap: Optional[float] = Field(None, description="Average price of a stock, weighted by volume")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "timestamp":"2026-01-12T10:25:00+00:00",
                "open":258.21,
                "high":259.19,
                "low":259.06,
                "close":259.15,
                "volume":1055,
                "trade_count":74,
                "vwap": 258.98
            }
        }


class StockTradingBulkInsert(BaseModel):
    """Bulk insert request for trading data"""
    timestamp: str = Field(..., description="Data timestamp")
    list: str = Field(..., description="Stock list category")
    name: str = Field(..., description="Stock name/ticker")
    last_price: Optional[float] = Field(None, description="Last traded price")
    change_abs: Optional[float] = Field(None, description="Absolute price change")
    change_pct: Optional[float] = Field(None, description="Percentage price change")
    highest: Optional[float] = Field(None, description="Highest price of the day")
    lowest: Optional[float] = Field(None, description="Lowest price of the day")
    volume: Optional[int] = Field(None, description="Trading volume")
    market_value: Optional[int] = Field(None, description="Market capitalization")
    href: Optional[str] = Field(None, description="URL to stock details")


class StockHistoricalBulkInsert(BaseModel):
    """Bulk insert request for historical data"""
    timestamp: str = Field(..., description="Data timestamp")
    list: str = Field(..., description="Stock list category")
    name: str = Field(..., description="Stock name/ticker")
    year_high: Optional[float] = Field(None, description="52-week high price")
    date_year_high: Optional[float] = Field(None, description="Price on this date previous 52-week")
    change_1d: Optional[float] = Field(None, description="1-day change %")
    change_1m: Optional[float] = Field(None, description="1-month change %")
    change_in_y: Optional[float] = Field(None, description="Year-to-date change %")
    change_1y: Optional[float] = Field(None, description="1-year change %")


class StockMetricsBulkInsert(BaseModel):
    """Bulk insert request for metrics data"""
    timestamp: str = Field(..., description="Data timestamp")
    list: str = Field(..., description="Stock list category")
    name: str = Field(..., description="Stock name/ticker")
    pe_ratio: Optional[float] = Field(None, description="Price-to-Earnings ratio")
    ps_ratio: Optional[float] = Field(None, description="Price-to-Sales ratio")
    earning_per_share: Optional[float] = Field(None, description="Earnings per share")
    equity_per_share: Optional[float] = Field(None, description="Equity per share")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield %")
    direct_return: Optional[float] = Field(None, description="Direct return %")


class BulkInsertRequest(BaseModel):
    """Request to bulk insert stock data"""
    trading: List[StockTradingBulkInsert] = Field(default_factory=list)
    historical: List[StockHistoricalBulkInsert] = Field(default_factory=list)
    metrics: List[StockMetricsBulkInsert] = Field(default_factory=list)
        

