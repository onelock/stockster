from playwright.sync_api import sync_playwright
import sqlite3
import datetime
import os
from data_utils import clean_number, clean_integer

# Get path relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(script_dir, "..", "db", "stocks_db.db")
DEBUG = 0

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    try:
        c = conn.cursor()
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=NORMAL")  # Faster writes, still safe with WAL
        c.execute("PRAGMA cache_size=-64000")  # 64MB cache
        
        # Current trading data (Kurser)
        c.execute("""
            CREATE TABLE IF NOT EXISTS stocks_trading (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                name TEXT NOT NULL,
                last_price REAL,
                change_abs REAL,
                change_pct REAL,
                highest REAL,
                lowest REAL,
                volume INTEGER,
                market_value INTEGER,
                href TEXT
            )
        """)
        
        # Create indexes for fast queries
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_name_timestamp 
            ON stocks_trading(name, timestamp DESC)
        """)
        
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_timestamp 
            ON stocks_trading(timestamp DESC)
        """)
        
        # Historical comparison data (Historik)
        c.execute("""
            CREATE TABLE IF NOT EXISTS stocks_historical (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                name TEXT NOT NULL,
                year_high REAL,
                date_year_high TEXT,
                change_1d REAL,
                change_1m REAL,
                change_in_y REAL,
                change_1y REAL
            )
        """)
        
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_historical_name_timestamp 
            ON stocks_historical(name, timestamp DESC)
        """)
        
        # Key metrics/ratios (Nyckeltal)
        c.execute("""
            CREATE TABLE IF NOT EXISTS stocks_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                name TEXT NOT NULL,
                pe_ratio REAL,
                ps_ratio REAL,
                earning_per_share REAL,
                equity_per_share REAL,
                dividend_yield REAL,
                direct_return REAL
            )
        """)
        
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
            ON stocks_metrics(name, timestamp DESC)
        """)
        
        conn.commit()
    finally:
        conn.close()

def scrape_disestockdata():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Increase timeout and add user agent to avoid blocks
        page.set_default_timeout(60000)  # 60 seconds
        
        try:
            page.goto("https://www.di.se/bors/aktier/?field=name&desc=false", wait_until="domcontentloaded")
            page.wait_for_selector("table", timeout=30000)
        except Exception as e:
            # print(f"Error loading page: {e}")
            browser.close()
            return

        # Scroll to load all content if page uses lazy loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)  # Wait for content to load
        
        # Find all tables by data-tab attribute
        tables = page.query_selector_all("table[data-tab]")
        # print(f"Found {len(tables)} total tables on the page")
        
        extracted = []
        
        # Helper function to process tables
        def process_table_type(table_selector, table_name, data_key):
            tables = page.query_selector_all(table_selector)
            # print(f"\nProcessing {len(tables)} instances of {table_name}")
            
            stock_idx = 0
            for table_idx, table in enumerate(tables):
                rows = table.query_selector_all("tbody tr")
                
                # print(f"  {table_name} instance {table_idx + 1}: {len(rows)} rows")
                
                for idx, row in enumerate(rows):
                    cols = row.query_selector_all("td")
                    row_data = [col.inner_text().strip() for col in cols]
                    
                    if not row_data:
                        continue
                    
                    # Debug: # print first row of first table
                    if DEBUG:
                        if idx == 0 and table_idx == 0:
                            print(f"    Sample row from {table_name}: {row_data[:3]}")
                    
                    if data_key == 'trading':
                    # Create new stock entry for trading data
                        link = row.query_selector("a")
                        stock = {
                            'name': row_data[0],
                            'href': link.get_attribute("href") if link else None,
                            'trading': row_data,
                            'historical': None,
                            'metrics': None
                        }
                        extracted.append(stock)
                    elif stock_idx < len(extracted):
                    # Add data to existing stock entry
                        extracted[stock_idx][data_key] = row_data
                        stock_idx += 1
            
            # print(f"Total stocks after {table_name}: {len(extracted)}")
        
        # Process all three table types
        process_table_type('table[data-tab="table_0"]', 'table_0 (Trading)', 'trading')
        process_table_type('table[data-tab="table_1"]', 'table_1 (Historical)', 'historical')
        process_table_type('table[data-tab="table_2"]', 'table_2 (Metrics)', 'metrics')

        browser.close()
        # print(f"\nExtracted {len(extracted)} stocks with all metrics")

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    for stock_index, stock in enumerate(extracted):
        href = stock['href']
        
        # Debug: # print what data we have for first stock
        if DEBUG:
            if stock_index == 0:
                print(f"  Trading (table_0): {stock['trading'][:3]} length: {len(stock['trading']) if stock['trading'] else None}")
                print(f"  Historical (table_1): {stock['historical'][:3]} length: {len(stock['historical']) if stock['historical'] else None}")
                print(f"  Metrics (table_2): {stock['metrics'][:3]} length: {len(stock['metrics']) if stock['metrics'] else None}")
        
        # Insert trading data
        if stock['trading'] and len(stock['trading']) >= 8:
            t = stock['trading']
            conn.execute("""
                INSERT INTO stocks_trading 
                (timestamp, name, last_price, change_abs, change_pct, highest, lowest, volume, market_value, href)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, 
                t[0],  # name
                clean_number(t[1]),  # last_price
                clean_number(t[2]),  # change_abs
                clean_number(t[3]),  # change_pct
                clean_number(t[4]),  # highest
                clean_number(t[5]),  # lowest
                clean_integer(t[6]),  # volume
                clean_integer(t[7]),  # market_value
                href
            ))
        
        # Insert historical data
        if stock['historical'] and len(stock['historical']) >= 7:
            h = stock['historical']
            conn.execute("""
                INSERT INTO stocks_historical
                (timestamp, name, year_high, date_year_high, change_1d, change_1m, change_in_y, change_1y)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                h[0],  # name
                clean_number(h[1]),  # year_high
                h[2],  # date_year_high
                clean_number(h[3]),  # change_1d
                clean_number(h[4]),  # change_1m
                clean_number(h[5]),  # change_in_y
                clean_number(h[6])   # change_1y
            ))
        
        # Insert metrics data
        if stock['metrics'] and len(stock['metrics']) >= 7:
            m = stock['metrics']
            conn.execute("""
                INSERT INTO stocks_metrics
                (timestamp, name, pe_ratio, ps_ratio, earning_per_share, equity_per_share, dividend_yield, direct_return)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                m[0],  # name
                clean_number(m[1]),  # pe_ratio
                clean_number(m[2]),  # ps_ratio
                clean_number(m[3]),  # earning_per_share
                clean_number(m[4]),  # equity_per_share
                clean_number(m[5]),  # dividend_yield
                clean_number(m[6])   # direct_return
            ))

    conn.commit()
    conn.close()
    # print(f"Data inserted into 3 separate tables")

if __name__ == "__main__":
    init_db()
    scrape_disestockdata()
