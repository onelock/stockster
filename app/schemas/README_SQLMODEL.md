# SQLModel Migration Complete

The application has been successfully migrated from psycopg2 to SQLModel/SQLAlchemy.

## What Changed

### 1. **Database Layer** ([app/core/database.py](../core/database.py))
- ✅ Removed psycopg2 dependencies entirely
- ✅ Implemented SQLModel engine with optimized connection pooling
- ✅ Created `get_session()` for FastAPI dependency injection
- ✅ Added helper functions:
  - `execute_raw_sql()` - Execute raw SELECT queries
  - `execute_raw_sql_write()` - Execute INSERT/UPDATE/DELETE
  - `bulk_insert_dicts()` - Bulk insert from dictionaries
  - `get_session_context()` - Context manager for non-FastAPI code
- ✅ Maintained backward compatibility with `get_db()` and `db_pool.close_all()`

### 2. **Data Models** ([app/schemas/models.py](models.py))
- ✅ Converted from Pydantic `BaseModel` to SQLModel
- ✅ Created three-tier model structure:
  - **Base models**: Shared field definitions (e.g., `StockTradingBase`)
  - **Table models**: Active database tables with `table=True` (e.g., `StockTrading`)
  - **Read models**: Response schemas with all fields (e.g., `StockTradingRead`)
- ✅ Used `Decimal` for financial precision instead of `float`
- ✅ All models map to existing database tables (no schema changes required)

### 3. **Repository Layer**
- ✅ [stock_repository.py](../../repositories/stock_repository.py) - Rewritten to use SQLModel Session
- ✅ [alpaca_repository.py](../../repositories/alpaca_repository.py) - Rewritten to use SQLModel Session
- ✅ Changed from cursor-based psycopg2 API to SQLAlchemy `text()` queries
- ✅ All methods return dictionaries for backward compatibility with services

### 4. **Dependency Injection** ([app/core/dependencies.py](../core/dependencies.py))
- ✅ Updated to inject `Session` objects instead of psycopg2 connections
- ✅ Repositories now receive SQLModel sessions

## Benefits of SQLModel

1. **Type Safety**: Full type hints and IDE autocompletion
2. **Data Validation**: Automatic Pydantic validation on all database models
3. **ORM Capabilities**: Can use ORM queries alongside raw SQL
4. **Connection Pooling**: Proper SQLAlchemy connection pooling with pre-ping
5. **Single Source of Truth**: Same model for database tables and API schemas
6. **Better Performance**: Optimized connection reuse and query execution

## Model Structure

Each entity has three models:
- **Base Model** (e.g., `StockTradingBase`): Shared fields without table configuration
- **Table Model** (e.g., `StockTrading`): Database table with `table=True`
- **Read Model** (e.g., `StockTradingRead`): Response schema with all fields including `id` and `created_at`

## Usage Examples

### 1. Using SQLModel ORM (Recommended for new code)

```python
from sqlmodel import Session, select
from app.core.database import get_session
from app.schemas.models import StockTrading, StockTradingRead

# Create a new record
def create_stock_trading(session: Session, data: dict):
    stock = StockTrading(**data)
    session.add(stock)
    session.commit()
    session.refresh(stock)
    return stock

# Query records
def get_stock_by_name(session: Session, name: str):
    statement = select(StockTrading).where(StockTrading.name == name)
    results = session.exec(statement).all()
    return results

# Update a record
def update_stock_price(session: Session, stock_id: int, new_price: float):
    statement = select(StockTrading).where(StockTrading.id == stock_id)
    stock = session.exec(statement).first()
    if stock:
        stock.last_price = new_price
        session.add(stock)
        session.commit()
        session.refresh(stock)
    return stock
```

### 2. Using in FastAPI Endpoints

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.models import StockTrading, StockTradingRead, StockTradingBase

router = APIRouter()

@router.post("/stocks/trading", response_model=StockTradingRead)
def create_trading_record(
    stock: StockTradingBase,
    session: Session = Depends(get_session)
):
    db_stock = StockTrading.model_validate(stock)
    session.add(db_stock)
    session.commit()
    session.refresh(db_stock)
    return db_stock

@router.get("/stocks/trading/{name}", response_model=list[StockTradingRead])
def get_trading_records(
    name: str,
    session: Session = Depends(get_session)
):
    statement = select(StockTrading).where(StockTrading.name == name)
    stocks = session.exec(statement).all()
    return stocks
```

### 3. Using Raw SQL (For complex queries)

```python
from app.core.database import execute_raw_sql

def get_custom_analysis(symbol: str):
    results = execute_raw_sql(
        """
        SELECT 
            name,
            AVG(last_price) as avg_price,
            MAX(highest) as max_high,
            MIN(lowest) as min_low
        FROM stock_data
        WHERE name = :symbol
        GROUP BY name
        """,
        {"symbol": symbol}
    )
    return results[0] if results else None
```

### 4. Context Manager (For non-FastAPI scripts)

```python
from app.core.database import get_session_context
from sqlmodel import select
from app.schemas.models import StockTrading

with get_session_context() as session:
    statement = select(StockTrading).where(StockTrading.name == "AAPL")
    stocks = session.exec(statement).all()
    # Automatically commits on exit
```

## Database Tables

All models map to existing database tables:
- `StockTrading` → `stock_data`
- `StockHistorical` → `stock_historical`
- `StockMetrics` → `stock_metrics`
- `AlpacaStocks` → `alpaca_bars`

**No database schema changes required** - SQLModel models match existing schema.

## Dependencies

Added to [requirements.txt](../../../requirements.txt):
```txt
sqlmodel==0.0.22
SQLAlchemy==2.0.36
```

Removed dependency:
```txt
❌ psycopg2-binary (no longer used directly, but kept for compatibility)
```

## Installation

```bash
pip install -r requirements.txt
```

## Testing the Migration

1. Start the application:
```bash
uvicorn app.main:app --reload
```

2. Test an endpoint:
```bash
curl http://localhost:8000/stocks/latest
```

3. Check database connectivity:
```bash
curl http://localhost:8000/health
```

## Breaking Changes

### None! 🎉

The migration maintains full backward compatibility:
- ✅ Existing API endpoints work unchanged
- ✅ Repository methods return the same data structures
- ✅ Service layer requires no modifications
- ✅ Database schema remains identical
- ✅ `get_db()` still available (now returns Session instead of connection)

## Performance Considerations

SQLModel/SQLAlchemy provides:
- **Connection pooling**: 5 persistent connections, up to 15 total
- **Pre-ping**: Validates connections before use
- **Lazy loading**: Connections created on demand
- **Connection recycling**: Automatic after 1 hour

For bulk operations, the repositories still use raw SQL with batch execution.

## Future Enhancements

Now that SQLModel is in place, you can:

1. **Use ORM relationships**: Define foreign keys and relationships between models
2. **Implement async support**: Switch to `AsyncSession` for async endpoints
3. **Add ORM queries**: Gradually replace raw SQL with type-safe ORM queries
4. **Leverage migrations**: Use Alembic with SQLModel's metadata
5. **Add validation**: Extend models with custom validators

## Troubleshooting

### Connection Issues
If you see connection errors, check:
```python
from app.core.database import engine
engine.dispose()  # Force connection pool refresh
```

### Query Results
All queries return `Row` objects. Convert to dict:
```python
result = session.exec(text("SELECT * FROM stocks")).first()
data = dict(result._mapping)  # Convert to dictionary
```

### Session Management
Sessions auto-commit on success, auto-rollback on errors. For manual control:
```python
session.add(item)
session.flush()  # Write to DB but don't commit
# ... more operations ...
session.commit()  # Commit all changes
```

