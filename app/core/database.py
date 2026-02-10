"""
Database connection and session management using SQLModel.
Provides both ORM session access and raw connection when needed.
"""
from typing import Generator
from contextlib import contextmanager
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from .config import settings


def get_database_url() -> str:
    """Construct PostgreSQL database URL from settings."""
    return (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )


def create_db_engine() -> Engine:
    """
    Create SQLModel/SQLAlchemy engine with optimized connection pooling.
    
    Pool settings:
    - pool_size: 5 connections always maintained
    - max_overflow: up to 10 additional connections when needed
    - pool_pre_ping: validate connections before use
    - pool_recycle: recycle connections after 1 hour
    """
    engine = create_engine(
        get_database_url(),
        echo=False,  # Set to True for SQL query logging in development
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections are alive before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        connect_args={
            "options": "-c timezone=utc"  # Ensure UTC timezone
        }
    )
    return engine


# Global engine instance - created once at module import
engine = create_db_engine()


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for SQLModel database sessions.
    
    Automatically handles:
    - Session creation and cleanup
    - Transaction commit on success
    - Transaction rollback on error
    - Connection return to pool
    
    Usage:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.exec(select(Item)).all()
            return items
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_db() -> Generator[Session, None, None]:
    """
    Alias for get_session() to maintain backward compatibility.
    Use get_session() for new code.
    """
    yield from get_session()


@contextmanager
def get_session_context():
    """
    Context manager for database sessions outside FastAPI context.
    
    Usage:
        with get_session_context() as session:
            items = session.exec(select(Item)).all()
            session.add(new_item)
            # Automatically commits on exit
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def execute_raw_sql(sql: str, params: dict = None) -> list:
    """
    Execute raw SQL query and return results.
    
    Args:
        sql: SQL query string (use :param for parameters)
        params: Dictionary of parameters for the query
    
    Returns:
        List of row dictionaries
        
    Usage:
        results = execute_raw_sql(
            "SELECT * FROM stocks WHERE name = :name",
            {"name": "AAPL"}
        )
    """
    with Session(engine) as session:
        result = session.exec(text(sql), params or {})
        return [dict(row._mapping) for row in result]


def execute_raw_sql_write(sql: str, params: dict = None) -> int:
    """
    Execute raw SQL write operation (INSERT, UPDATE, DELETE).
    
    Args:
        sql: SQL command string (use :param for parameters)
        params: Dictionary of parameters for the command
    
    Returns:
        Number of rows affected
        
    Usage:
        rows = execute_raw_sql_write(
            "DELETE FROM stocks WHERE timestamp < :date",
            {"date": cutoff_date}
        )
    """
    with Session(engine) as session:
        result = session.exec(text(sql), params or {})
        session.commit()
        return result.rowcount


def bulk_insert_dicts(table_name: str, records: list[dict]) -> int:
    """
    Bulk insert multiple records into a table.
    
    Args:
        table_name: Name of the table to insert into
        records: List of dictionaries with column: value pairs
    
    Returns:
        Number of records inserted
        
    Usage:
        records = [
            {"name": "AAPL", "price": 150.0},
            {"name": "GOOGL", "price": 2800.0}
        ]
        count = bulk_insert_dicts("stocks", records)
    """
    if not records:
        return 0
    
    # Get column names from first record
    columns = list(records[0].keys())
    column_str = ", ".join(columns)
    placeholders = ", ".join([f":{col}" for col in columns])
    
    sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
    
    with Session(engine) as session:
        for record in records:
            session.exec(text(sql), record)
        session.commit()
    
    return len(records)


def create_db_and_tables():
    """
    Create all tables defined in SQLModel models.
    
    ⚠️  WARNING: Only use this for testing or initial development setup.
    For production, always use Alembic migrations to manage schema changes.
    
    Usage:
        # In a test setup or initialization script
        from app.schemas.models import *  # Import all table models
        create_db_and_tables()
    """
    SQLModel.metadata.create_all(engine)


def drop_db_and_tables():
    """
    Drop all tables defined in SQLModel models.
    
    ⚠️  DANGER: This permanently deletes all data!
    Only use in testing or development environments.
    """
    SQLModel.metadata.drop_all(engine)


def close_db_connections():
    """
    Close all database connections and dispose of the engine.
    Call this during application shutdown.
    """
    engine.dispose()


# Alias for backward compatibility
class DatabasePool:
    """Legacy compatibility class - use get_session() instead."""
    
    @staticmethod
    def close_all():
        """Close all database connections."""
        close_db_connections()


# Global instance for backward compatibility with main.py
db_pool = DatabasePool()

