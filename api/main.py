"""
FastAPI service for accessing stock data from PostgreSQL database
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

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
    """Get database connection"""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
        database=os.environ.get('POSTGRES_DB', 'stockster'),
        user=os.environ.get('POSTGRES_USER', 'stockster'),
        password=os.environ.get('POSTGRES_PASSWORD', ''),
        cursor_factory=RealDictCursor
    )

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
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/stocks")
def get_all_stocks(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all stocks with latest trading data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT ON (name) 
                name, last_price, change_abs, change_pct, 
                highest, lowest, volume, market_value, 
                timestamp, href
            FROM stocks_trading
            ORDER BY name, timestamp DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
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
def get_latest_stocks(limit: int = Query(50, ge=1, le=500)):
    """Get latest stock data snapshot"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the latest timestamp
        cursor.execute("SELECT MAX(timestamp) as latest FROM stocks_trading")
        latest_time = cursor.fetchone()['latest']
        
        if not latest_time:
            return {"stocks": [], "timestamp": None}
        
        cursor.execute("""
            SELECT name, last_price, change_abs, change_pct, 
                   highest, lowest, volume, market_value, 
                   timestamp, href
            FROM stocks_trading
            WHERE timestamp = %s
            ORDER BY market_value DESC NULLS LAST
            LIMIT %s
        """, (latest_time, limit))
        
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT name, last_price, change_abs, change_pct, 
                   highest, lowest, volume, market_value, 
                   timestamp, href
            FROM stocks_trading
            WHERE name = %s AND timestamp >= %s
            ORDER BY timestamp DESC
        """, (stock_name, cutoff_date))
        
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT name, period_1w, period_1m, period_3m, 
                   period_ytd, period_1y, period_3y, 
                   period_5y, period_10y, timestamp, href
            FROM stocks_historical
            WHERE name = %s AND timestamp >= %s
            ORDER BY timestamp DESC
        """, (stock_name, cutoff_date))
        
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT name, pe_ratio, ps_ratio, earning_per_share, 
                   equity_per_share, dividend_yield, direct_return, 
                   timestamp
            FROM stocks_metrics
            WHERE name = %s AND timestamp >= %s
            ORDER BY timestamp DESC
        """, (stock_name, cutoff_date))
        
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT name
            FROM stocks_trading
            WHERE name ILIKE %s
            ORDER BY name
            LIMIT 50
        """, (f"%{q}%",))
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            "query": q,
            "count": len(results),
            "results": [r['name'] for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_database_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count stocks
        cursor.execute("SELECT COUNT(DISTINCT name) as total_stocks FROM stocks_trading")
        total_stocks = cursor.fetchone()['total_stocks']
        
        # Count total records
        cursor.execute("SELECT COUNT(*) as total_records FROM stocks_trading")
        total_records = cursor.fetchone()['total_records']
        
        # Get date range
        cursor.execute("SELECT MIN(timestamp) as first_date, MAX(timestamp) as last_date FROM stocks_trading")
        date_range = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_stocks": total_stocks,
            "total_records": total_records,
            "first_date": date_range['first_date'],
            "last_date": date_range['last_date']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
