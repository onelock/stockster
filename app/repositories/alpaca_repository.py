"""
PostgreSQL repository for Alpaca stock data access using SQLModel.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session
from sqlalchemy import text


class AlpacaRepository:
    """Repository for Alpaca stock data operations using SQLModel/SQLAlchemy."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_all_symbols(self, limit: int = 100, offset: int = 0) -> List[str]:
        """Get all unique stock symbols."""
        query = text("""
            SELECT DISTINCT symbol
            FROM alpaca_bars
            ORDER BY symbol
            LIMIT :limit OFFSET :offset
        """)
        result = self.session.exec(query, {"limit": limit, "offset": offset})
        return [row.symbol for row in result]
    
    def get_symbol_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical trading data for a specific symbol."""
        since = datetime.now() - timedelta(days=days)
        
        query = text("""
            SELECT symbol, timestamp, open, high, low, close,
                   volume, trade_count, vwap
            FROM alpaca_bars
            WHERE symbol = :symbol AND timestamp >= :since
            ORDER BY timestamp DESC
        """)
        result = self.session.exec(query, {"symbol": symbol, "since": since})
        return [dict(row._mapping) for row in result]
    
    def get_latest_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the most recent trading data for a symbol."""
        query = text("""
            SELECT symbol, timestamp, open, high, low, close,
                   volume, trade_count, vwap
            FROM alpaca_bars
            WHERE symbol = :symbol
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        result = self.session.exec(query, {"symbol": symbol}).first()
        return dict(result._mapping) if result else None
    
    def get_latest_for_all_symbols(self) -> List[Dict[str, Any]]:
        """Get the most recent data for all symbols."""
        query = text("""
            SELECT DISTINCT ON (symbol)
                symbol, timestamp, open, high, low, close,
                volume, trade_count, vwap
            FROM alpaca_bars
            ORDER BY symbol, timestamp DESC
        """)
        result = self.session.exec(query)
        return [dict(row._mapping) for row in result]
    
    def get_data_by_date_range(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get trading data for a symbol within a date range."""
        query = text("""
            SELECT symbol, timestamp, open, high, low, close,
                   volume, trade_count, vwap
            FROM alpaca_bars
            WHERE symbol = :symbol 
              AND timestamp >= :start_date 
              AND timestamp <= :end_date
            ORDER BY timestamp DESC
        """)
        result = self.session.exec(
            query, 
            {"symbol": symbol, "start_date": start_date, "end_date": end_date}
        )
        return [dict(row._mapping) for row in result]
    
    def get_ohlc_aggregated(
        self, 
        symbol: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated OHLC data for a symbol."""
        since = datetime.now() - timedelta(days=days)
        
        query = text("""
            SELECT 
                symbol,
                MIN(open) as min_open,
                MAX(high) as max_high,
                MIN(low) as min_low,
                AVG(close) as avg_close,
                SUM(volume) as total_volume,
                SUM(trade_count) as total_trades,
                AVG(vwap) as avg_vwap,
                COUNT(*) as data_points
            FROM alpaca_bars
            WHERE symbol = :symbol AND timestamp >= :since
            GROUP BY symbol
        """)
        result = self.session.exec(query, {"symbol": symbol, "since": since}).first()
        return dict(result._mapping) if result else {}
    
    def search_symbols(self, query: str) -> List[str]:
        """Search for symbols by partial match."""
        sql = text("""
            SELECT DISTINCT symbol
            FROM alpaca_bars
            WHERE symbol ILIKE :query
            ORDER BY symbol
            LIMIT 20
        """)
        result = self.session.exec(sql, {"query": f"%{query}%"})
        return [row.symbol for row in result]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for Alpaca data."""
        query = text("""
            SELECT 
                COUNT(DISTINCT symbol) as total_symbols,
                COUNT(*) as total_records,
                MIN(timestamp) as first_date,
                MAX(timestamp) as last_date
            FROM alpaca_bars
        """)
        result = self.session.exec(query).first()
        return dict(result._mapping) if result else {}
    
    def get_top_volume_symbols(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get symbols with highest trading volume."""
        since = datetime.now() - timedelta(days=days)
        
        query = text("""
            SELECT 
                symbol,
                SUM(volume) as total_volume,
                SUM(trade_count) as total_trades,
                AVG(vwap) as avg_vwap
            FROM alpaca_bars
            WHERE timestamp >= :since
            GROUP BY symbol
            ORDER BY total_volume DESC
            LIMIT :limit
        """)
        result = self.session.exec(query, {"since": since, "limit": limit})
        return [dict(row._mapping) for row in result]
    
    def check_connection(self) -> bool:
        """Check if database connection is alive."""
        try:
            self.session.exec(text("SELECT 1"))
            return True
        except Exception:
            return False
