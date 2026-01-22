"""
Business logic service for volatility analysis.
"""
from typing import List, Dict, Any
from ..repositories.stock_repository import StockRepository
import statistics


class VolatilityService:
    """Service layer for stock volatility calculations."""
    
    def __init__(self, repository: StockRepository):
        self.repository = repository
    
    def calculate_volatility(self, name: str, days: int = 30) -> Dict[str, Any]:
        """Calculate volatility metrics for a stock."""
        stocks_data = self.repository.get_stock_by_name(name, days)
        
        if not stocks_data or len(stocks_data) < 2:
            return None
        
        # Extract price changes
        price_changes = [
            stock['change_pct'] 
            for stock in stocks_data 
            if stock.get('change_pct') is not None
        ]
        
        if not price_changes:
            return None
        
        # Calculate statistics
        avg_change = statistics.mean(price_changes)
        std_dev = statistics.stdev(price_changes) if len(price_changes) > 1 else 0
        max_change = max(price_changes)
        min_change = min(price_changes)
        
        return {
            "name": name,
            "days": days,
            "average_change_pct": round(avg_change, 2),
            "volatility_std_dev": round(std_dev, 2),
            "max_change_pct": round(max_change, 2),
            "min_change_pct": round(min_change, 2),
            "data_points": len(price_changes)
        }
    
    def get_most_volatile(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most volatile stocks."""
        # This would require getting all stocks and calculating volatility
        # Simplified implementation for now
        stocks_data = self.repository.get_all_stocks(limit=1000, offset=0)
        
        volatility_list = []
        for stock_info in stocks_data:
            vol = self.calculate_volatility(stock_info['name'], days)
            if vol:
                volatility_list.append(vol)
        
        # Sort by volatility (std_dev) descending
        volatility_list.sort(key=lambda x: x['volatility_std_dev'], reverse=True)
        
        return volatility_list[:limit]