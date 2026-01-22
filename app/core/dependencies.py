"""
Dependency injection for the application.
"""
from typing import Generator
from fastapi import Depends
from .database import get_db
from ..repositories.stock_repository import StockRepository
from ..repositories.alpaca_repository import AlpacaRepository
from ..services.stock_service import StockService
from ..services.volatility_service import VolatilityService
from ..services.alpaca_service import AlpacaService


# Repository Dependencies
def get_stock_repository(conn=Depends(get_db)) -> StockRepository:
    """Provide StockRepository instance."""
    return StockRepository(conn)

def get_alpaca_repository(conn=Depends(get_db)) -> AlpacaRepository:
    """Provide AlpacaRepository instance."""
    return AlpacaRepository(conn)

# Service Dependencies
def get_stock_service(
    repository: StockRepository = Depends(get_stock_repository)
) -> StockService:
    """Provide StockService instance."""
    return StockService(repository)


def get_volatility_service(
    repository: StockRepository = Depends(get_stock_repository)
) -> VolatilityService:
    """Provide VolatilityService instance."""
    return VolatilityService(repository)

def get_alpaca_service(
    repository: AlpacaRepository = Depends(get_alpaca_repository)
) -> AlpacaService :
    """Provide AlpacaService instance."""
    return AlpacaService(repository)