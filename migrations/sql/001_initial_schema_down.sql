-- Drop indexes first
DROP INDEX IF EXISTS idx_alpaca_bars_symbol_timestamp;
DROP INDEX IF EXISTS idx_alpaca_bars_timestamp;
DROP INDEX IF EXISTS idx_alpaca_bars_symbol;

DROP INDEX IF EXISTS idx_stock_metrics_name_timestamp;
DROP INDEX IF EXISTS idx_stock_metrics_timestamp;
DROP INDEX IF EXISTS idx_stock_metrics_name;

DROP INDEX IF EXISTS idx_stock_historical_name_timestamp;
DROP INDEX IF EXISTS idx_stock_historical_timestamp;
DROP INDEX IF EXISTS idx_stock_historical_name;

DROP INDEX IF EXISTS idx_stock_data_list;
DROP INDEX IF EXISTS idx_stock_data_name_timestamp;
DROP INDEX IF EXISTS idx_stock_data_timestamp;
DROP INDEX IF EXISTS idx_stock_data_name;

-- Drop tables
DROP TABLE IF EXISTS alpaca_bars;
DROP TABLE IF EXISTS stock_metrics;
DROP TABLE IF EXISTS stock_historical;
DROP TABLE IF EXISTS stock_data;
