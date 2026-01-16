"""DI Stock Scraper - Fetches stock data from di.se"""
from playwright.sync_api import sync_playwright
import datetime
import os
import csv
from data_utils import clean_number, clean_integer

DEBUG = 0
CSV_OUTPUT_DIR = os.getenv('CSV_OUTPUT_DIR', '/data')

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
    
    # Ensure output directory exists
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
    
    # Prepare data for CSV export
    trading_data = []
    historical_data = []
    metrics_data = []
    
    for stock in extracted:
        href = stock['href']
        
        # Prepare trading data
        if stock['trading'] and len(stock['trading']) >= 8:
            t = stock['trading']
            trading_data.append({
                'timestamp': timestamp,
                'name': t[0],
                'last_price': clean_number(t[1]),
                'change_abs': clean_number(t[2]),
                'change_pct': clean_number(t[3]),
                'highest': clean_number(t[4]),
                'lowest': clean_number(t[5]),
                'volume': clean_integer(t[6]),
                'market_value': clean_integer(t[7]),
                'href': href
            })
        
        # Prepare historical data
        if stock['historical'] and len(stock['historical']) >= 7:
            h = stock['historical']
            historical_data.append({
                'timestamp': timestamp,
                'name': h[0],
                'year_high': clean_number(h[1]),
                'date_year_high': h[2],
                'change_1d': clean_number(h[3]),
                'change_1m': clean_number(h[4]),
                'change_in_y': clean_number(h[5]),
                'change_1y': clean_number(h[6])
            })
        
        # Prepare metrics data
        if stock['metrics'] and len(stock['metrics']) >= 7:
            m = stock['metrics']
            metrics_data.append({
                'timestamp': timestamp,
                'name': m[0],
                'pe_ratio': clean_number(m[1]),
                'ps_ratio': clean_number(m[2]),
                'earning_per_share': clean_number(m[3]),
                'equity_per_share': clean_number(m[4]),
                'dividend_yield': clean_number(m[5]),
                'direct_return': clean_number(m[6])
            })
    
    # Write or append to trading CSV
    if trading_data:
        csv_file = os.path.join(CSV_OUTPUT_DIR, 'stocks_trading.csv')
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=trading_data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(trading_data)
        print(f"{'Appended' if file_exists else 'Created'} {len(trading_data)} trading records to {csv_file}")
    
    # Write or append to historical CSV
    if historical_data:
        csv_file = os.path.join(CSV_OUTPUT_DIR, 'stocks_historical.csv')
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=historical_data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(historical_data)
        print(f"{'Appended' if file_exists else 'Created'} {len(historical_data)} historical records to {csv_file}")
    
    # Write or append to metrics CSV
    if metrics_data:
        csv_file = os.path.join(CSV_OUTPUT_DIR, 'stocks_metrics.csv')
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=metrics_data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(metrics_data)
        print(f"{'Appended' if file_exists else 'Created'} {len(metrics_data)} metrics records to {csv_file}")

if __name__ == "__main__":
    scrape_disestockdata()
