"""
Business logic service for Alpaca stock operations.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from ..repositories.alpaca_repository import AlpacaRepository
from ..schemas.alpaca_models import AlpacaBar, AlpacaOHLCAggregated, AlpacaVolumeData
from ..schemas.alpaca_responses import (
    AlpacaSymbolsListResponse,
    AlpacaBarsResponse,
    AlpacaLatestBarsResponse,
    AlpacaOHLCResponse,
    AlpacaTopVolumeResponse,
    AlpacaSearchResponse,
    AlpacaDatabaseStats
)


class AlpacaService:
    """Service layer for Alpaca stock business logic."""
    
    def __init__(self, repository: AlpacaRepository):
        self.repository = repository
    
    def get_symbols_list(self, limit: int = 100, offset: int = 0) -> AlpacaSymbolsListResponse:
        """Get paginated list of symbols."""
        symbols = self.repository.get_all_symbols(limit, offset)
        
        return AlpacaSymbolsListResponse(
            count=len(symbols),
            limit=limit,
            offset=offset,
            symbols=symbols
        )
    
    def get_symbol_bars(self, symbol: str, days: int = 30) -> Optional[AlpacaBarsResponse]:
        """Get bar data for a specific symbol."""
        bars_data = self.repository.get_symbol_data(symbol, days)
        
        if not bars_data:
            return None
        
        bars = [AlpacaBar(**bar) for bar in bars_data]
        
        return AlpacaBarsResponse(
            symbol=symbol,
            days=days,
            count=len(bars),
            bars=bars
        )
    
    def get_latest_bar(self, symbol: str) -> Optional[AlpacaBar]:
        """Get the most recent bar for a symbol."""
        bar_data = self.repository.get_latest_data(symbol)
        
        if not bar_data:
            return None
        
        return AlpacaBar(**bar_data)
    
    def get_latest_all_symbols(self) -> AlpacaLatestBarsResponse:
        """Get latest bars for all symbols."""
        bars_data = self.repository.get_latest_for_all_symbols()
        bars = [AlpacaBar(**bar) for bar in bars_data]
        
        return AlpacaLatestBarsResponse(
            count=len(bars),
            bars=bars
        )
    
    def get_bars_by_date_range(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[AlpacaBarsResponse]:
        """Get bars for a symbol within a date range."""
        bars_data = self.repository.get_data_by_date_range(symbol, start_date, end_date)
        
        if not bars_data:
            return None
        
        bars = [AlpacaBar(**bar) for bar in bars_data]
        days = (end_date - start_date).days
        
        return AlpacaBarsResponse(
            symbol=symbol,
            days=days,
            count=len(bars),
            bars=bars
        )
    
    def get_ohlc_aggregated(self, symbol: str, days: int = 30) -> Optional[AlpacaOHLCResponse]:
        """Get aggregated OHLC data for a symbol."""
        ohlc_data = self.repository.get_ohlc_aggregated(symbol, days)
        
        if not ohlc_data:
            return None
        
        ohlc = AlpacaOHLCAggregated(**ohlc_data)
        
        return AlpacaOHLCResponse(
            symbol=symbol,
            days=days,
            data=ohlc
        )
    
    def get_top_volume_symbols(self, days: int = 7, limit: int = 10) -> AlpacaTopVolumeResponse:
        """Get symbols with highest trading volume."""
        volume_data = self.repository.get_top_volume_symbols(days, limit)
        symbols = [AlpacaVolumeData(**data) for data in volume_data]
        
        return AlpacaTopVolumeResponse(
            days=days,
            count=len(symbols),
            symbols=symbols
        )
    
    def search_symbols(self, query: str) -> AlpacaSearchResponse:
        """Search for symbols by partial match."""
        symbols = self.repository.search_symbols(query)
        
        return AlpacaSearchResponse(
            query=query,
            count=len(symbols),
            symbols=symbols
        )
    
    def get_stats(self) -> AlpacaDatabaseStats:
        """Get database statistics for Alpaca data."""
        stats = self.repository.get_database_stats()
        return AlpacaDatabaseStats(**stats)
