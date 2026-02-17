"""
Core SQLModel data models for stock data entities.
"""

from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class StockTradingBase(SQLModel):
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


class StockTrading(StockTradingBase, table=True):
    """Trading data table model"""
    __tablename__ = "stock_data"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
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
                "href": "/bors/aktier/abb-730/",
                "created_at": "2026-01-16T14:15:21"
            }
        }
    }


class StockTradingRead(StockTradingBase):
    """Trading data read schema"""
    id: int
    created_at: datetime



class StockHistoricalBase(SQLModel):
    """Base historical comparison data for a stock"""
    name: str = Field(index=True, max_length=100, description="Stock name/ticker")
    ath: Optional[Decimal] = Field(None, description="52-week high price", max_digits=12, decimal_places=2)
    date_ath: Optional[datetime] = Field(None, description="Date of 52-week all-time high")
    one_day_change: Optional[Decimal] = Field(None, description="1-day change %", max_digits=8, decimal_places=2)
    one_month_change: Optional[Decimal] = Field(None, description="1-month change %", max_digits=8, decimal_places=2)
    year_to_date_change: Optional[Decimal] = Field(None, description="Year-to-date change %", max_digits=8, decimal_places=2)
    one_year_change: Optional[Decimal] = Field(None, description="1-year change %", max_digits=8, decimal_places=2)
    list: Optional[str] = Field(None, max_length=100, description="Market Capital list of stock")
    timestamp: datetime = Field(index=True, description="Data timestamp")


class StockHistorical(StockHistoricalBase, table=True):
    """Historical comparison table model"""
    __tablename__ = "stock_historical"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    model_config = {
            "json_schema_extra": {
                "example": {
                    "id": 1,
                    "name": "ABB",
                    "ath": 726.4,
                    "date_ath": "2026-01-16",
                    "one_day_change": -0.34,
                    "one_month_change": 3.61,
                    "year_to_date_change": 2.05,
                    "one_year_change": 2.62,
                    "list": "Large Cap",
                    "timestamp": "2026-01-16T14:15:21",
                    "created_at": "2026-01-16T14:15:21"
                }
            }
        }

class StockHistoricalRead(StockHistoricalBase):
    """Historical data read schema"""
    id: int
    created_at: datetime

class StockMetricsBase(SQLModel):
    """Base financial metrics for a stock"""
    name: str = Field(index=True, max_length=100, description="Stock name/ticker")
    pe_ratio: Optional[Decimal] = Field(None, description="Price-to-Earnings ratio", max_digits=12, decimal_places=2)
    ps_ratio: Optional[Decimal] = Field(None, description="Price-to-Sales ratio", max_digits=12, decimal_places=2)
    earning_per_share: Optional[Decimal] = Field(None, description="Earnings per share", max_digits=12, decimal_places=2)
    equity_per_share: Optional[Decimal] = Field(None, description="Equity per share", max_digits=12, decimal_places=2)
    dividend_yield: Optional[Decimal] = Field(None, description="Dividend yield %", max_digits=8, decimal_places=2)
    direct_return: Optional[Decimal] = Field(None, description="Direct return %", max_digits=8, decimal_places=2)
    list: Optional[str] = Field(None, max_length=100, description="Market Capital list of stock")
    timestamp: datetime = Field(index=True, description="Data timestamp")


class StockMetrics(StockMetricsBase, table=True):
    """Financial metrics table model"""
    __tablename__ = "stock_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "ABB",
                "pe_ratio": 30.0,
                "ps_ratio": 3.58,
                "earning_per_share": 23.6,
                "equity_per_share": 90.32,
                "dividend_yield": 10.94,
                "direct_return": 2.8,
                "list": "Large Cap",
                "timestamp": "2026-01-16T14:15:21",
                "created_at": "2026-01-16T14:15:21"
            }
        }
    }

class StockMetricsRead(StockMetricsBase):
    """Metrics data read schema"""
    id: int
    created_at: datetime


class AlpacaStocksBase(SQLModel):
    """Base Alpaca stock bar data"""
    symbol: str = Field(index=True, max_length=20, description="Stock name/ticker")
    timestamp: datetime = Field(index=True, description="Data timestamp")
    open: Optional[Decimal] = Field(None, description="Opening stock price", max_digits=12, decimal_places=4)
    high: Optional[Decimal] = Field(None, description="Highest stock price", max_digits=12, decimal_places=4)
    low: Optional[Decimal] = Field(None, description="Lowest stock price", max_digits=12, decimal_places=4)
    close: Optional[Decimal] = Field(None, description="Closing stock price", max_digits=12, decimal_places=4)
    volume: Optional[int] = Field(None, description="Total number of shares")
    trade_count: Optional[int] = Field(None, description="Total number of trades")
    vwap: Optional[Decimal] = Field(None, description="Average price of a stock, weighted by volume", max_digits=12, decimal_places=4)


class AlpacaStocks(AlpacaStocksBase, table=True):
    """Alpaca bars table model"""
    __tablename__ = "alpaca_bars"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Record creation timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "symbol": "AAPL",
                "timestamp": "2026-01-12T10:25:00+00:00",
                "open": 258.21,
                "high": 259.19,
                "low": 259.06,
                "close": 259.15,
                "volume": 1055,
                "trade_count": 74,
                "vwap": 258.98,
                "created_at": "2026-01-16T14:15:21"
            }
        }
    }


class AlpacaStocksRead(AlpacaStocksBase):
    """Alpaca bars read schema"""
    id: int
    created_at: datetime


class BulkInsertRequest(SQLModel):
    trading: List[StockTradingBase] = Field(default_factory=list)
    historical: List[StockHistoricalBase] = Field(default_factory=list)
    metrics: List[StockMetricsBase] = Field(default_factory=list)
        

