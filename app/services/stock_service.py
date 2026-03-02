"""
Business logic service for stock operations.
"""
from typing import List, Optional
from datetime import datetime
from ..repositories.stock_repository import StockRepository
from ..schemas import (
    StockTrading, StockHistorical, StockMetrics,
    StocksListResponse, LatestStocksResponse,
    StockDetailResponse, StockHistoricalResponse,
    StockMetricsResponse, SearchResponse, DatabaseStats
)


class StockService:
    """Service layer for stock business logic."""
    
    def __init__(self, repository: StockRepository):
        self.repository = repository
    
    def get_stocks_list(self, limit: int = 100, offset: int = 0) -> StocksListResponse:
        """Get paginated list of stocks."""
        stocks_data = self.repository.get_all_stocks(limit, offset)
        stocks = [StockTrading(**stock) for stock in stocks_data]
        
        return StocksListResponse(
            count=len(stocks),
            limit=limit,
            offset=offset,
            data=stocks,
        )
    
    def get_latest_stocks(self) -> LatestStocksResponse:
        """Get latest snapshot of all stocks."""
        timestamp, stocks_data = self.repository.get_latest_stocks()
        stocks = [StockTrading(**stock) for stock in stocks_data]
        
        return LatestStocksResponse(
            timestamp=timestamp,
            count=len(stocks),
            data=stocks
        )
    
    def get_stock_detail(self, name: str, days: int = 30) -> Optional[StockDetailResponse]:
        """Get detailed stock data."""
        stocks_data = self.repository.get_stock_by_name(name, days)
        
        if not stocks_data:
            return None
        
        stocks = [StockTrading(**stock) for stock in stocks_data]
        
        return StockDetailResponse(
            name=name,
            days=days,
            count=len(stocks),
            data=stocks
        )
    
    def get_stock_historical(self, name: str, days: int = 30) -> Optional[StockHistoricalResponse]:
        """Get historical comparison data."""
        historical_data = self.repository.get_stock_historical(name, days)
        
        if not historical_data:
            return None
        
        historical = [StockHistorical(**h) for h in historical_data]
        
        return StockHistoricalResponse(
            name=name,
            days=days,
            count=len(historical),
            data=historical
        )
    
    def get_stock_metrics(self, name: str, days: int = 30) -> Optional[StockMetricsResponse]:
        """Get financial metrics data."""
        metrics_data = self.repository.get_stock_metrics(name, days)
        
        if not metrics_data:
            return None
        
        metrics = [StockMetrics(**m) for m in metrics_data]
        
        return StockMetricsResponse(
            name=name,
            days=days,
            count=len(metrics),
            data=metrics
        )
    
    def search_stocks(self, query: str) -> SearchResponse:
        """Search for stocks by name."""
        results = self.repository.search_stocks(query)
        
        return SearchResponse(
            query=query,
            count=len(results),
            results=results
        )
    
    def get_stats(self) -> DatabaseStats:
        """Get database statistics."""
        stats = self.repository.get_database_stats()
        return DatabaseStats(**stats)
    
    def bulk_insert_data(self, trading_data: List[dict], 
                        historical_data: List[dict], 
                        metrics_data: List[dict]) -> dict:
        """Bulk insert stock data from scraper."""
        trading_count = self.repository.bulk_insert_trading(trading_data)
        historical_count = self.repository.bulk_insert_historical(historical_data)
        metrics_count = self.repository.bulk_insert_metrics(metrics_data)
        
        return {
            "trading_inserted": trading_count,
            "historical_inserted": historical_count,
            "metrics_inserted": metrics_count,
            "total_inserted": trading_count + historical_count + metrics_count
        }