"""
Database connection pool management for PostgreSQL.
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from .config import settings


class DatabasePool:
    """Singleton database connection pool."""
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
                cursor_factory=RealDictCursor
            )
    
    def get_connection(self):
        """Get a connection from the pool."""
        return self._pool.getconn()
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        self._pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()


# Global pool instance
db_pool = DatabasePool()


def get_db():
    """
    Dependency for database connections.
    Automatically returns connection to pool after use.
    """
    conn = db_pool.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.return_connection(conn)


@contextmanager
def get_db_context():
    """
    Context manager for database connections (for non-FastAPI usage).
    Automatically returns connection to pool after use.
    """
    conn = db_pool.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.return_connection(conn)

