"""Database connection utilities supporting both SQLite and PostgreSQL"""
import os
import sqlite3

def get_db_connection():
    """Get database connection based on environment variables"""
    db_type = os.environ.get('DATABASE_TYPE', 'sqlite')
    
    if db_type == 'postgresql':
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=os.environ.get('POSTGRES_PORT', '5432'),
            database=os.environ.get('POSTGRES_DB', 'stockster'),
            user=os.environ.get('POSTGRES_USER', 'stockster'),
            password=os.environ.get('POSTGRES_PASSWORD', ''),
        )
        return conn, 'postgresql'
    else:
        # Default to SQLite
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.environ.get('DB_PATH', os.path.join(script_dir, "..", "db", "stocks_db.db"))
        conn = sqlite3.connect(db_path, timeout=10.0)
        return conn, 'sqlite'

def init_db():
    """Initialize database schema"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if db_type == 'sqlite':
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")
        
        # Current trading data (Kurser)
        if db_type == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks_trading (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    name TEXT NOT NULL,
                    last_price REAL,
                    change_abs REAL,
                    change_pct REAL,
                    highest REAL,
                    lowest REAL,
                    volume BIGINT,
                    market_value BIGINT,
                    href TEXT
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks_trading (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    last_price REAL,
                    change_abs REAL,
                    change_pct REAL,
                    highest REAL,
                    lowest REAL,
                    volume INTEGER,
                    market_value INTEGER,
                    href TEXT
                )
            """)
        
        # Create indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_name_timestamp 
            ON stocks_trading(name, timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_timestamp 
            ON stocks_trading(timestamp DESC)
        """)
        
        # Historical comparison data (Historik)
        if db_type == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks_historical (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    name TEXT NOT NULL,
                    period_1w REAL,
                    period_1m REAL,
                    period_3m REAL,
                    period_ytd REAL,
                    period_1y REAL,
                    period_3y REAL,
                    period_5y REAL,
                    period_10y REAL,
                    href TEXT
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks_historical (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    period_1w REAL,
                    period_1m REAL,
                    period_3m REAL,
                    period_ytd REAL,
                    period_1y REAL,
                    period_3y REAL,
                    period_5y REAL,
                    period_10y REAL,
                    href TEXT
                )
            """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_historical_name_timestamp 
            ON stocks_historical(name, timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_historical_timestamp 
            ON stocks_historical(timestamp DESC)
        """)
        
        conn.commit()
        return conn, db_type
        
    except Exception as e:
        conn.rollback()
        raise e
