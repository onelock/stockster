"""
FastAPI service for accessing stock data from PostgreSQL database
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path so we can import analysis module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.config import DATABASE_TYPE, SQLITE_DB_PATH, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

app = FastAPI(
    title="Stockster API",
    description="REST API for accessing Swedish stock market data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get database connection based on configuration"""
    if DATABASE_TYPE == 'sqlite':
        import sqlite3
        conn = sqlite3.connect(SQLITE_DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'
    else:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn, 'postgresql'

def execute_query(cursor, query, params=None, db_type='postgresql'):
    """Execute query with appropriate parameter style for database type"""
    if db_type == 'sqlite' and params:
        # Convert PostgreSQL %s placeholders to SQLite ? placeholders
        query = query.replace('%s', '?')
    cursor.execute(query, params or ())
    return cursor

@app.get("/")
def root():
    """API root endpoint"""
    return {
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

@app.get("/health")
def health():
    """Health check endpoint"""
    try:
        conn, db_type = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected", "db_type": db_type}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/stocks")
def get_all_stocks(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all stocks with latest trading data"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Use compatible query for both SQLite and PostgreSQL
        execute_query(cursor, """
            SELECT s1.name, s1.last_price, s1.change_abs, s1.change_pct, 
                   s1.highest, s1.lowest, s1.volume, s1.market_value, 
                   s1.timestamp, s1.href
            FROM stocks_trading s1
            INNER JOIN (
                SELECT name, MAX(timestamp) as max_ts
                FROM stocks_trading
                GROUP BY name
            ) s2 ON s1.name = s2.name AND s1.timestamp = s2.max_ts
            ORDER BY s1.name
            LIMIT %s OFFSET %s
        """, (limit, offset), db_type)
        
        stocks = cursor.fetchall()
        conn.close()
        
        return {
            "count": len(stocks),
            "limit": limit,
            "offset": offset,
            "stocks": stocks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/latest")
def get_latest_stocks(limit: int = Query(50, ge=1, le=5000)):
    """Get latest stock data snapshot"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Get the latest timestamp
        execute_query(cursor, "SELECT MAX(timestamp) as latest FROM stocks_trading", None, db_type)
        result = cursor.fetchone()
        latest_time = result['latest'] if db_type == 'postgresql' else result[0]
        
        if not latest_time:
            return {"stocks": [], "timestamp": None}
        
        # Build ORDER BY clause based on database type
        if db_type == 'postgresql':
            order_clause = "ORDER BY market_value DESC NULLS LAST"
        else:
            # SQLite: NULL values are considered smaller than any other value
            order_clause = "ORDER BY CASE WHEN market_value IS NULL THEN 1 ELSE 0 END, market_value DESC"
        
        query = f"""
            SELECT name, last_price, change_abs, change_pct, 
                   highest, lowest, volume, market_value, 
                   timestamp, href
            FROM stocks_trading
            WHERE timestamp = %s
            {order_clause}
            LIMIT %s
        """
        
        execute_query(cursor, query, (latest_time, limit), db_type)
        
        stocks = cursor.fetchall()
        conn.close()
        
        return {
            "timestamp": latest_time,
            "count": len(stocks),
            "stocks": stocks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{stock_name}")
def get_stock(stock_name: str, days: int = Query(7, ge=1, le=365)):
    """Get stock data for specific stock over time"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        execute_query(cursor, """
            SELECT name, last_price, change_abs, change_pct, 
                   highest, lowest, volume, market_value, 
                   timestamp, href
            FROM stocks_trading
            WHERE name = %s AND timestamp >= %s
            ORDER BY timestamp DESC
        """, (stock_name, cutoff_date), db_type)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Stock '{stock_name}' not found")
        
        return {
            "name": stock_name,
            "days": days,
            "count": len(data),
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{stock_name}/historical")
def get_stock_historical(stock_name: str, days: int = Query(30, ge=1, le=365)):
    """Get historical comparison data for specific stock"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        execute_query(cursor, """
            SELECT name, period_1w, period_1m, period_3m, 
                   period_ytd, period_1y, period_3y, 
                   period_5y, period_10y, timestamp, href
            FROM stocks_historical
            WHERE name = %s AND timestamp >= %s
            ORDER BY timestamp DESC
        """, (stock_name, cutoff_date), db_type)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Historical data for '{stock_name}' not found")
        
        return {
            "name": stock_name,
            "days": days,
            "count": len(data),
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{stock_name}/metrics")
def get_stock_metrics(stock_name: str, days: int = Query(30, ge=1, le=365)):
    """Get key metrics/ratios for specific stock"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        execute_query(cursor, """
            SELECT name, pe_ratio, ps_ratio, earning_per_share, 
                   equity_per_share, dividend_yield, direct_return, 
                   timestamp
            FROM stocks_metrics
            WHERE name = %s AND timestamp >= %s
            ORDER BY timestamp DESC
        """, (stock_name, cutoff_date), db_type)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Metrics for '{stock_name}' not found")
        
        return {
            "name": stock_name,
            "days": days,
            "count": len(data),
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search_stocks(q: str = Query(..., min_length=1)):
    """Search stocks by name"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Use LIKE for SQLite, ILIKE for PostgreSQL
        like_operator = "LIKE" if db_type == 'sqlite' else "ILIKE"
        query = f"""
            SELECT DISTINCT name
            FROM stocks_trading
            WHERE name {like_operator} %s
            ORDER BY name
            LIMIT 50
        """
        
        execute_query(cursor, query, (f"%{q}%",), db_type)
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            "query": q,
            "count": len(results),
            "results": [r['name'] if db_type == 'postgresql' else r[0] for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_database_stats():
    """Get database statistics"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Count stocks
        execute_query(cursor, "SELECT COUNT(DISTINCT name) as total_stocks FROM stocks_trading", None, db_type)
        result = cursor.fetchone()
        total_stocks = result['total_stocks'] if db_type == 'postgresql' else result[0]
        
        # Count total records
        execute_query(cursor, "SELECT COUNT(*) as total_records FROM stocks_trading", None, db_type)
        result = cursor.fetchone()
        total_records = result['total_records'] if db_type == 'postgresql' else result[0]
        
        # Get date range
        execute_query(cursor, "SELECT MIN(timestamp) as first_date, MAX(timestamp) as last_date FROM stocks_trading", None, db_type)
        date_range = cursor.fetchone()
        
        conn.close()
        
        if db_type == 'postgresql':
            return {
                "total_stocks": total_stocks,
                "total_records": total_records,
                "first_date": date_range['first_date'],
                "last_date": date_range['last_date']
            }
        else:
            return {
                "total_stocks": total_stocks,
                "total_records": total_records,
                "first_date": date_range[0],
                "last_date": date_range[1]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
