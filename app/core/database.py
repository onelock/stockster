"""
Database connection and session management using SQLModel.
Provides both ORM session access and raw connection when needed.
"""
from typing import Generator
from sqlmodel import create_engine, Session
from sqlalchemy.engine import Engine
from .config import settings


def get_database_url() -> str:
    """Construct PostgreSQL database URL from settings."""
    return (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password.get_secret_value()}"
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


