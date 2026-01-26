"""
PostgreSQL repository for stock data access.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


class StockRepository:
    """Repository for stock data operations using PostgreSQL."""
    
    def __init__(self, conn):
        self.conn = conn
    
    def get_all_stocks(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all stocks with pagination."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (name)
                    name, last_price, change_abs, change_pct,
                    highest, lowest, volume, market_value, list,
                    timestamp, href
                FROM stock_data
                ORDER BY name, timestamp DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()
    
    def get_latest_stocks(self) -> tuple[Optional[datetime], List[Dict[str, Any]]]:
        """Get the latest snapshot of all stocks."""
        with self.conn.cursor() as cur:
            # Get latest timestamp
            cur.execute("SELECT MAX(timestamp) FROM stock_data")
            latest_time = cur.fetchone()['max']
            
            if not latest_time:
                return None, []
            
            # Get all stocks at that timestamp
            cur.execute("""
                SELECT name, last_price, change_abs, change_pct,
                       highest, lowest, volume, market_value, list,
                       timestamp, href
                FROM stock_data
                WHERE timestamp = %s
                ORDER BY name
            """, (latest_time,))
            
            return latest_time, cur.fetchall()
    
    def get_stock_by_name(self, name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get stock data for a specific stock."""
        since = datetime.now() - timedelta(days=days)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT name, last_price, change_abs, change_pct,
                       highest, lowest, volume, market_value, list,
                       timestamp, href
                FROM stock_data
                WHERE name = %s AND timestamp >= %s
                ORDER BY timestamp DESC
            """, (name, since))
            return cur.fetchall()
    
    def get_stock_historical(self, name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical comparison data for a stock."""
        since = datetime.now() - timedelta(days=days)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT name, year_high, date_year_high,
                       period_1d, period_1m, period_ytd, period_1y, list,
                       timestamp
                FROM stock_historical
                WHERE name = %s AND timestamp >= %s
                ORDER BY timestamp DESC
            """, (name, since))
            return cur.fetchall()
    
    def get_stock_metrics(self, name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get financial metrics for a stock."""
        since = datetime.now() - timedelta(days=days)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT name, pe_ratio, ps_ratio, earning_per_share,
                       equity_per_share, dividend_yield, direct_return, list,
                       timestamp
                FROM stock_metrics
                WHERE name = %s AND timestamp >= %s
                ORDER BY timestamp DESC
            """, (name, since))
            return cur.fetchall()
    
    def search_stocks(self, query: str) -> List[str]:
        """Search for stocks by name."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT name
                FROM stock_data
                WHERE name ILIKE %s
                ORDER BY name
                LIMIT 20
            """, (f"%{query}%",))
            return [row['name'] for row in cur.fetchall()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT name) as total_stocks,
                    COUNT(*) as total_records,
                    MIN(timestamp) as first_date,
                    MAX(timestamp) as last_date
                FROM stock_data
            """)
            return cur.fetchone()
    
    def check_connection(self) -> bool:
        """Check if database connection is alive."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception:
            return False    
    def bulk_insert_trading(self, trading_data: List[Dict[str, Any]]) -> int:
        """Bulk insert trading data."""
        if not trading_data:
            return 0
        
        with self.conn.cursor() as cur:
            # Use ON CONFLICT to handle duplicates
            cur.executemany("""
                INSERT INTO stock_data 
                    (name, last_price, change_abs, change_pct, highest, lowest, 
                     volume, market_value, timestamp, href, list)
                VALUES (%(name)s, %(last_price)s, %(change_abs)s, %(change_pct)s, 
                        %(highest)s, %(lowest)s, %(volume)s, %(market_value)s, 
                        %(timestamp)s, %(href)s, %(list)s)
                ON CONFLICT (name, timestamp) 
                DO UPDATE SET
                    last_price = EXCLUDED.last_price,
                    change_abs = EXCLUDED.change_abs,
                    change_pct = EXCLUDED.change_pct,
                    highest = EXCLUDED.highest,
                    lowest = EXCLUDED.lowest,
                    volume = EXCLUDED.volume,
                    market_value = EXCLUDED.market_value,
                    href = EXCLUDED.href,
                    list = EXCLUDED.list
            """, trading_data)
            self.conn.commit()
            return len(trading_data)
    
    def bulk_insert_historical(self, historical_data: List[Dict[str, Any]]) -> int:
        """Bulk insert historical data."""
        if not historical_data:
            return 0
        
        with self.conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO stock_historical
                    (name, year_high, date_year_high, period_1d, period_1m, 
                     period_ytd, period_1y, timestamp, list)
                VALUES (%(name)s, %(year_high)s, %(date_year_high)s, %(change_1d)s, 
                        %(change_1m)s, %(change_in_y)s, %(change_1y)s, %(timestamp)s, %(list)s)
                ON CONFLICT (name, timestamp)
                DO UPDATE SET
                    year_high = EXCLUDED.year_high,
                    date_year_high = EXCLUDED.date_year_high,
                    period_1d = EXCLUDED.period_1d,
                    period_1m = EXCLUDED.period_1m,
                    period_ytd = EXCLUDED.period_ytd,
                    period_1y = EXCLUDED.period_1y,
                    list = EXCLUDED.list
            """, historical_data)
            self.conn.commit()
            return len(historical_data)
    
    def bulk_insert_metrics(self, metrics_data: List[Dict[str, Any]]) -> int:
        """Bulk insert metrics data."""
        if not metrics_data:
            return 0
        
        with self.conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO stock_metrics
                    (name, pe_ratio, ps_ratio, earning_per_share, equity_per_share,
                     dividend_yield, direct_return, timestamp, list)
                VALUES (%(name)s, %(pe_ratio)s, %(ps_ratio)s, %(earning_per_share)s,
                        %(equity_per_share)s, %(dividend_yield)s, %(direct_return)s,
                        %(timestamp)s, %(list)s)
                ON CONFLICT (name, timestamp)
                DO UPDATE SET
                    pe_ratio = EXCLUDED.pe_ratio,
                    ps_ratio = EXCLUDED.ps_ratio,
                    earning_per_share = EXCLUDED.earning_per_share,
                    equity_per_share = EXCLUDED.equity_per_share,
                    dividend_yield = EXCLUDED.dividend_yield,
                    direct_return = EXCLUDED.direct_return,
                    list = EXCLUDED.list
            """, metrics_data)
            self.conn.commit()
            return len(metrics_data)