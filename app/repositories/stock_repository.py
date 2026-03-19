"""
PostgreSQL repository for stock data access using SQLModel.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select

from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import insert

from ..schemas.models import StockTrading, StockHistorical, StockMetrics


class StockRepository:
    """Repository for stock data operations using SQLModel/SQLAlchemy."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_all_stocks(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all stocks with pagination."""
        
        query = (
            select(StockTrading)
            .distinct(StockTrading.name)
            .order_by(StockTrading.name)
            .limit(limit)
            .offset(offset)
            )
        
        result = self.session.exec(query)
        return [dict(row) for row in result]
    
    def get_latest_stocks(self) -> tuple[Optional[datetime], List[Dict[str, Any]]]:
        """Get the latest snapshot of all stocks."""
        # Get latest timestamp
        time_query = select(StockTrading).order_by(StockTrading.timestamp.desc()).limit(1)
        time_result = self.session.exec(time_query).first()
        latest_time = time_result.timestamp if time_result else None
        
        if not latest_time:
            return None, []
        
        # Get all stocks at that timestamp
        query = (
            select(StockTrading)
            .distinct(StockTrading.name)
            .where(StockTrading.timestamp <= latest_time)
            .order_by(StockTrading.name)
        )
        result = self.session.exec(query)
        stocks = [dict(row) for row in result]
        
        return  latest_time, stocks
    
    def get_stock_by_name(self, name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get stock data for a specific stock."""
        since = datetime.now() - timedelta(days=days)
        query =(
            select(StockTrading)
            .where(func.lower(StockTrading.name).contains(name.lower()))
            .where(StockTrading.timestamp >= since)
            .order_by(StockTrading.timestamp.desc())
        )
        result = self.session.exec(query)
        return [dict(row) for row in result]
    
    def get_stock_historical(self, name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical comparison data for a stock."""
        since = datetime.now() - timedelta(days=days)
        
        query = (
            select(StockHistorical)
            .where(func.lower(StockHistorical.name).contains(name.lower()))
            .where(StockHistorical.timestamp >= since)
            .order_by(StockHistorical.timestamp.desc())
        )
        result = self.session.exec(query)
        return [dict(row) for row in result]
    
    def get_stock_metrics(self, name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get financial metrics for a stock."""
        since = datetime.now() - timedelta(days=days)
        
        query = (
            select(StockMetrics)
            .where(func.lower(StockMetrics.name).contains(name.lower()))
            .where(StockMetrics.timestamp >= since)
            .order_by(StockMetrics.timestamp.desc())
        )
        result = self.session.exec(query)
        return [dict(row) for row in result]
    
    def search_stocks(self, name: str) -> List[str]:
        """Search for stocks by name."""
        query = (
            select(StockTrading)
            .distinct(StockTrading.name)
            .where(func.lower(StockTrading.name).contains(name.lower()))
            .order_by(StockTrading.name)
            .limit(20)
        )
        result = self.session.exec(query)
        return [row.name for row in result]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        
        query = (
            select(
                func.count(func.distinct(StockTrading.name)).label("total_stocks"),
                func.count().label("total_records"),
                func.min(StockTrading.timestamp).label("first_date"),
                func.max(StockTrading.timestamp).label("last_date")
            )
        )

        result = self.session.exec(query).first()
        return dict(result._mapping) if result else {}
    
    def check_connection(self) -> bool:
        """Check if database connection is alive."""
        try:
            self.session.exec(text("SELECT 1"))
            return True
        except Exception:
            return False    


    def bulk_insert(self, model: Any, data: List[Dict[str, Any]]) -> int:
        
        if not data:
            return 0

        unique_data = { (row['name'], row['timestamp']): row for row in data }
        
        deduped_data = list(unique_data.values())
        stmt = insert(model).values(deduped_data)
        
        # update_cols = {}
        # for col in model.__table__.columns:
        #     if col.name not in ['name', 'timestamp', 'id']:
        #         update_cols[col.name] = stmt.excluded[col.name]

        upsert_stmt = stmt.on_conflict_do_nothing(
            index_elements=['name', 'timestamp']
            # set_=update_cols
        )

        
        try:
            self.session.exec(upsert_stmt)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"❌ Database Error: {e}")
            raise e
        
        return len(data)
    
    def bulk_insert_trading(self, data: List[Dict[str, Any]]) -> int:
        """Bulk upsert trading data using SQLAlchemy Core."""
        return self.bulk_insert(StockTrading, data)
    
    def bulk_insert_historical(self, data: List[Dict[str, Any]]) -> int:
        """Bulk insert historical data."""
        return self.bulk_insert(StockHistorical, data)
    
    def bulk_insert_metrics(self, data: List[Dict[str, Any]]) -> int:
        """Bulk insert metrics data."""
        return self.bulk_insert(StockMetrics, data)
    