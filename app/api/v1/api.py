"""
API v1 router aggregation.
"""
from fastapi import APIRouter
from .endpoints import stocks, volatility, health, alpaca_stocks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(stocks.router)
api_router.include_router(volatility.router)
api_router.include_router(health.router)
# api_router.include_router(alpaca_stocks.router)