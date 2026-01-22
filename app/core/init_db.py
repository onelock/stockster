#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL.
Creates tables and indexes for the stockster application.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from .config import settings


def create_database():
    """Create the database if it doesn't exist."""
    # Connect to default postgres database
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            database='postgres',
            user=settings.postgres_user,
            password=settings.postgres_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor() as cur:
                # Check if database exists
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (settings.postgres_db,)
                )
                exists = cur.fetchone()
                
                if not exists:
                    cur.execute(f"CREATE DATABASE {settings.postgres_db}")
                    print(f"✅ Database '{settings.postgres_db}' created successfully")
                else:
                    print(f"ℹ️  Database '{settings.postgres_db}' already exists")
        finally:
            conn.close()
    except Exception as e:
        print(f"⚠️  Could not create database: {e}")


def create_tables():
    """Create all required tables."""
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password
    )
    
    try:
        with conn.cursor() as cur:
            # Create stock_data table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    last_price DECIMAL(12, 2),
                    change_abs DECIMAL(12, 2),
                    change_pct DECIMAL(8, 2),
                    highest DECIMAL(12, 2),
                    lowest DECIMAL(12, 2),
                    volume BIGINT,
                    market_value BIGINT,
                    timestamp TIMESTAMP NOT NULL,
                    href TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_stock_timestamp UNIQUE (name, timestamp)
                )
            """)
            print("✅ Table 'stock_data' created/verified")
            
            # Create stock_historical table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_historical (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    year_high DECIMAL(12, 2),
                    date_year_high DECIMAL(12, 2),
                    period_1d DECIMAL(8, 2),
                    period_1m DECIMAL(8, 2),
                    period_ytd DECIMAL(8, 2),
                    period_1y DECIMAL(8, 2),
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_historical_timestamp UNIQUE (name, timestamp)
                )
            """)
            print("✅ Table 'stock_historical' created/verified")
            
            # Create stock_metrics table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_metrics (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    pe_ratio DECIMAL(12, 2),
                    ps_ratio DECIMAL(12, 2),
                    earning_per_share DECIMAL(12, 2),
                    equity_per_share DECIMAL(12, 2),
                    dividend_yield DECIMAL(8, 2),
                    direct_return DECIMAL(8, 2),
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_metrics_timestamp UNIQUE (name, timestamp)
                )
            """)
            print("✅ Table 'stock_metrics' created/verified")
            
            conn.commit()
    finally:
        conn.close()


def create_indexes():
    """Create indexes for better query performance."""
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password
    )
    
    try:
        with conn.cursor() as cur:
            # Indexes for stock_data
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_data_name 
                ON stock_data(name)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_data_timestamp 
                ON stock_data(timestamp DESC)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_data_name_timestamp 
                ON stock_data(name, timestamp DESC)
            """)
            print("✅ Indexes created for 'stock_data'")
            
            # Indexes for stock_historical
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_historical_name 
                ON stock_historical(name)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_historical_timestamp 
                ON stock_historical(timestamp DESC)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_historical_name_timestamp 
                ON stock_historical(name, timestamp DESC)
            """)
            print("✅ Indexes created for 'stock_historical'")
            
            # Indexes for stock_metrics
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_metrics_name 
                ON stock_metrics(name)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_metrics_timestamp 
                ON stock_metrics(timestamp DESC)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_metrics_name_timestamp 
                ON stock_metrics(name, timestamp DESC)
            """)
            print("✅ Indexes created for 'stock_metrics'")
            
            conn.commit()
    finally:
        conn.close()


def init_database():
    """Initialize the complete database setup."""
    try:
        print("🔧 Initializing PostgreSQL database...")
        print(f"📍 Host: {settings.postgres_host}:{settings.postgres_port}")
        print(f"📊 Database: {settings.postgres_db}")
        print(f"👤 User: {settings.postgres_user}")
        print()
        
        create_database()
        create_tables()
        create_indexes()
        
        print()
        print("🎉 Database initialization completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    init_database()
