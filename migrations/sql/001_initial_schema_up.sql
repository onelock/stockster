-- Create stock_data table
CREATE TABLE IF NOT EXISTS stock_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    last_price DECIMAL(12, 2),
    change_abs DECIMAL(12, 2),
    change_pct DECIMAL(8, 2),
    highest DECIMAL(12, 2),
    lowest DECIMAL(12, 2),
    volume BIGINT,
    market_value BIGINT,
    timestamp TIMESTAMP NOT NULL,
    href TEXT,
    list VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_stock_timestamp UNIQUE (name, timestamp)
);

-- Create stock_historical table
CREATE TABLE IF NOT EXISTS stock_historical (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    year_high DECIMAL(12, 2),
    date_year_high DECIMAL(12, 2),
    period_1d DECIMAL(8, 2),
    period_1m DECIMAL(8, 2),
    period_ytd DECIMAL(8, 2),
    period_1y DECIMAL(8, 2),
    timestamp TIMESTAMP NOT NULL,
    list VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_historical_timestamp UNIQUE (name, timestamp)
);

-- Create stock_metrics table
CREATE TABLE IF NOT EXISTS stock_metrics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    pe_ratio DECIMAL(12, 2),
    ps_ratio DECIMAL(12, 2),
    earning_per_share DECIMAL(12, 2),
    equity_per_share DECIMAL(12, 2),
    dividend_yield DECIMAL(8, 2),
    direct_return DECIMAL(8, 2),
    timestamp TIMESTAMP NOT NULL,
    list VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_metrics_timestamp UNIQUE (name, timestamp)
);

-- Create indexes for stock_data
CREATE INDEX IF NOT EXISTS idx_stock_data_name ON stock_data(name);
CREATE INDEX IF NOT EXISTS idx_stock_data_timestamp ON stock_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stock_data_name_timestamp ON stock_data(name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stock_data_list ON stock_data(list);

-- Create indexes for stock_historical
CREATE INDEX IF NOT EXISTS idx_stock_historical_name ON stock_historical(name);
CREATE INDEX IF NOT EXISTS idx_stock_historical_timestamp ON stock_historical(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stock_historical_name_timestamp ON stock_historical(name, timestamp DESC);

-- Create indexes for stock_metrics
CREATE INDEX IF NOT EXISTS idx_stock_metrics_name ON stock_metrics(name);
CREATE INDEX IF NOT EXISTS idx_stock_metrics_timestamp ON stock_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stock_metrics_name_timestamp ON stock_metrics(name, timestamp DESC);

-- Create Alpaca tables
CREATE TABLE IF NOT EXISTS alpaca_bars (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    volume BIGINT,
    trade_count INTEGER,
    vwap DECIMAL(12, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_alpaca_symbol_timestamp UNIQUE (symbol, timestamp)
);

-- Create indexes for alpaca_bars
CREATE INDEX IF NOT EXISTS idx_alpaca_bars_symbol ON alpaca_bars(symbol);
CREATE INDEX IF NOT EXISTS idx_alpaca_bars_timestamp ON alpaca_bars(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alpaca_bars_symbol_timestamp ON alpaca_bars(symbol, timestamp DESC);

-- Create comments for documentation
COMMENT ON TABLE stock_data IS 'Main stock trading data from DI.se scraper';
COMMENT ON TABLE stock_historical IS 'Historical comparison data for stocks';
COMMENT ON TABLE stock_metrics IS 'Financial metrics and ratios for stocks';
COMMENT ON TABLE alpaca_bars IS 'OHLCV bar data from Alpaca API';
