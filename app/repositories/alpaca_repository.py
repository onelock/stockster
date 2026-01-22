"""
PostgreSQL repository for Alpaca stock data access.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


class AlpacaRepository:
    """Repository for Alpaca stock data operations using PostgreSQL."""
    
    def __init__(self, conn):
        self.conn = conn
    
    def get_all_symbols(self, limit: int = 100, offset: int = 0) -> List[str]:
        """Get all unique stock symbols."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT symbol
                FROM alpaca_stocks_trading
                ORDER BY symbol
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return [row['symbol'] for row in cur.fetchall()]
    
    def get_symbol_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical trading data for a specific symbol."""
        since = datetime.now() - timedelta(days=days)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT symbol, timestamp, open, high, low, close,
                       volume, trade_count, vwap
                FROM alpaca_stocks_trading
                WHERE symbol = %s AND timestamp::timestamp >= %s
                ORDER BY timestamp DESC
            """, (symbol, since))
            return cur.fetchall()
    
    def get_latest_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the most recent trading data for a symbol."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT symbol, timestamp, open, high, low, close,
                       volume, trade_count, vwap
                FROM alpaca_stocks_trading
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol,))
            return cur.fetchone()
    
    def get_latest_for_all_symbols(self) -> List[Dict[str, Any]]:
        """Get the most recent data for all symbols."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (symbol)
                    symbol, timestamp, open, high, low, close,
                    volume, trade_count, vwap
                FROM alpaca_stocks_trading
                ORDER BY symbol, timestamp DESC
            """)
            return cur.fetchall()
    
    def get_data_by_date_range(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get trading data for a symbol within a date range."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT symbol, timestamp, open, high, low, close,
                       volume, trade_count, vwap
                FROM alpaca_stocks_trading
                WHERE symbol = %s 
                  AND timestamp::timestamp >= %s 
                  AND timestamp::timestamp <= %s
                ORDER BY timestamp DESC
            """, (symbol, start_date, end_date))
            return cur.fetchall()
    
    def get_ohlc_aggregated(
        self, 
        symbol: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated OHLC data for a symbol."""
        since = datetime.now() - timedelta(days=days)
        
        with self.conn.cursor() as cur:
            cur.execute("""
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
                FROM alpaca_stocks_trading
                WHERE symbol = %s AND timestamp::timestamp >= %s
                GROUP BY symbol
            """, (symbol, since))
            return cur.fetchone()
    
    def search_symbols(self, query: str) -> List[str]:
        """Search for symbols by partial match."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT symbol
                FROM alpaca_stocks_trading
                WHERE symbol ILIKE %s
                ORDER BY symbol
                LIMIT 20
            """, (f"%{query}%",))
            return [row['symbol'] for row in cur.fetchall()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for Alpaca data."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT symbol) as total_symbols,
                    COUNT(*) as total_records,
                    MIN(timestamp) as first_date,
                    MAX(timestamp) as last_date
                FROM alpaca_stocks_trading
            """)
            return cur.fetchone()
    
    def get_top_volume_symbols(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get symbols with highest trading volume."""
        since = datetime.now() - timedelta(days=days)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    symbol,
                    SUM(volume) as total_volume,
                    SUM(trade_count) as total_trades,
                    AVG(vwap) as avg_vwap
                FROM alpaca_stocks_trading
                WHERE timestamp::timestamp >= %s
                GROUP BY symbol
                ORDER BY total_volume DESC
                LIMIT %s
            """, (since, limit))
            return cur.fetchall()
    
    def check_connection(self) -> bool:
        """Check if database connection is alive."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception:
            return False
