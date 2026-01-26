from playwright.sync_api import sync_playwright
import datetime
import os
import csv
from urllib.parse import urljoin
import requests
import json

CSV_OUTPUT_DIR = os.getenv('CSV_OUTPUT_DIR', '/data')
BASE_URL = "https://www.di.se/bors/aktier/"
API_URL = os.getenv('API_URL', 'http://localhost:8000/api/v1')
API_ENABLED = os.getenv('API_ENABLED', 'true').lower() == 'true'
WRITE_TO_CSV_ENABLED=os.getenv('WRITE_TO_CSV_ENABLED', 'false').lower() == 'true'

def clean_number(s):
    if not s or s == '-':
        return None
    s = s.replace(',', '.').replace(' ', '').replace('\xa0', '')
    s = s.replace('%', '').replace('kr', '').strip()
    try:
        return float(s)
    except:
        return None

def clean_integer(s):
    if not s or s == '-':
        return None
    s = s.replace(',', '').replace(' ', '').replace('\xa0', '').strip()
    try:
        return int(s)
    except:
        return None

def write_to_csv(dir, data, filename, mode='a'):
    """Write data to CSV file"""
    csv_file = os.path.join(dir, filename)
    with open(csv_file, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        if mode == 'w' or not os.path.exists(csv_file):
            writer.writeheader()
        writer.writerows(data)
    print(f"✅ {'Created' if mode == 'w' else 'Appended'} {len(data)} records → {csv_file}")

def send_to_api(trading_data, historical_data, metrics_data):
    """Send scraped data to API"""
    try:
        api_endpoint = f"{API_URL}/stocks/bulk"
        payload = {
            "trading": trading_data,
            "historical": historical_data,
            "metrics": metrics_data
        }
        
        print(f"\n📡 Sending data to API: {api_endpoint}")
        print(f"   - Trading records: {len(trading_data)}")
        print(f"   - Historical records: {len(historical_data)}")
        print(f"   - Metrics records: {len(metrics_data)}")
        
        response = requests.post(
            api_endpoint, 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response: {result.get('message', 'Success')}")
            print(f"   - Trading inserted: {result.get('trading_inserted', 0)}")
            print(f"   - Historical inserted: {result.get('historical_inserted', 0)}")
            print(f"   - Metrics inserted: {result.get('metrics_inserted', 0)}")
            print(f"   - Total inserted: {result.get('total_inserted', 0)}")
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send data to API: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending to API: {e}")
        return False
def scroll_to_load_all(page, max_scrolls=20, scroll_pause=1):
    """
    Scroll page incrementally to trigger lazy loading.
    Stops when no new content appears.
    """
    # print("  🔄 Scrolling to load all content...")
    
    last_height = page.evaluate("document.body.scrollHeight")
    scroll_count = 0
    no_change_count = 0
    
    while scroll_count < max_scrolls:
        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for potential lazy load
        page.wait_for_timeout(scroll_pause * 1000)
        
        # Check if new content loaded
        new_height = page.evaluate("document.body.scrollHeight")
        
        if new_height == last_height:
            no_change_count += 1
            if no_change_count >= 3:
                # print(f"  ✅ Content fully loaded after {scroll_count + 1} scrolls")
                break
        else:
            no_change_count = 0
        
        last_height = new_height
        scroll_count += 1
    
    return scroll_count

def scrape_tables_from_page(page, page_name, list_name):
    """
    Scrape all tables from the current page.
    Returns dict with table data organized by table index.
    """
    # print(f"\n{'='*60}")
    # print(f"📄 Scraping page: {page_name} (List: {list_name})")
    # print(f"{'='*60}")
    
    # Wait for tables to load
    try:
        page.wait_for_selector("table", timeout=1000)
    except:
        print("  ⚠️  No tables found on this page")
        return {}
    
    # Scroll to load all content
    scroll_to_load_all(page, max_scrolls=20, scroll_pause=1)
    
    # Find all tables
    tables = page.query_selector_all("table[data-tab]")
    # print(f"  📊 Found {len(tables)} tables")
    
    page_data = {}
    
    for table_idx in range(3):  # table_0, table_1, table_2
        table_selector = f'table[data-tab="table_{table_idx}"]'
        tables = page.query_selector_all(table_selector)
        
        if not tables:
            print(f"  ⚠️  table_{table_idx} not found")
            continue
        
        table_name = ['Trading', 'Historical', 'Metrics'][table_idx]
        all_rows = []
        
        for table in tables:
            rows = table.query_selector_all("tbody tr")
            
            for row in rows:
                cols = row.query_selector_all("td")
                row_data = [col.inner_text().strip() for col in cols]
                
                if not row_data or len(row_data) < 2:
                    continue
                
                # Get href for trading table (table_0)
                href = None
                if table_idx == 0:
                    link = row.query_selector("a")
                    href = link.get_attribute("href") if link else None
                
                all_rows.append({
                    'name': row_data[0],
                    'data': row_data,
                    'href': href,
                    'list': list_name  # Add list identifier
                })
        
        page_data[f'table_{table_idx}'] = all_rows
        # print(f"  ✅ {table_name} (table_{table_idx}): {len(all_rows)} rows")
    
    return page_data

def scrape_disestockdata():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.set_default_timeout(15000)
        
        try:
            print(f"📡 Loading {BASE_URL}")
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
            print("✅ Initial page loaded")
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            browser.close()
            return
        
        # Find the submenu
        # print("\n🔍 Looking for submenu (aria-label='Undermeny')...")
        submenu = page.query_selector('[aria-label="Undermeny"]')
        
        if not submenu:
            print("❌ Submenu not found!")
            browser.close()
            return
        
        # Get the first 4 links from the submenu
        menu_links = submenu.query_selector_all("a")[:4]
        
        if not menu_links:
            print("❌ No links found in submenu!")
            browser.close()
            return
        
        # print(f"✅ Found {len(menu_links)} menu items to scrape")
        
        # Extract link info before clicking - use inner text as list name
        menu_items = []
        for link in menu_links:
            text = link.inner_text().strip()
            href = link.get_attribute("href")
            
            # Convert relative URL to absolute URL
            full_url = urljoin(BASE_URL, href)
            
            menu_items.append({
                'text': text,
                'href': full_url,  # Store absolute URL
                'list': text  # Use the link text as the list name
            })
            # print(f"  - List: '{text}' → {full_url}")
        
        # Scrape each menu page
        all_pages_data = {}
        
        for idx, item in enumerate(menu_items, 1):
            # print(f"\n{'='*60}")
            # print(f"📑 Menu Item {idx}/{len(menu_items)}: {item['text']}")
            # print(f"{'='*60}")
            
            try:
                # Navigate to the page
                page.goto(item['href'], wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                
                # Scrape tables from this page with list name
                page_data = scrape_tables_from_page(page, item['text'], item['list'])
                
                if page_data:
                    all_pages_data[item['text']] = {
                        'data': page_data,
                        'list': item['list']
                    }
                
            except Exception as e:
                print(f"  ❌ Error scraping {item['text']}: {e}")
                continue
        
        browser.close()
    
    # Process and save all collected data
    # print(f"\n{'='*60}")
    # print("💾 Processing collected data...")
    # print(f"{'='*60}")
    
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d')
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
    
    # Combine data from all pages
    all_trading_data = []
    all_historical_data = []
    all_metrics_data = []
    
    # Expected counts per list
    expected_counts = {
        menu_items[0]['list']: 160,
        menu_items[1]['list']: 139,
        menu_items[2]['list']: 109,
        menu_items[3]['list']: 354
    }
    
    for page_name, page_info in all_pages_data.items():
        page_data = page_info['data']
        list_name = page_info['list']
        
        # print(f"\n📄 Processing: {page_name} (List: {list_name})")
        
        trading_rows = page_data.get('table_0', [])
        historical_rows = page_data.get('table_1', [])
        metrics_rows = page_data.get('table_2', [])
        
        # Verify expected count
        expected = expected_counts.get(list_name, 0)
        actual = len(trading_rows)
        status = "✅" if actual == expected else "⚠️"
        # print(f"  {status} Expected {expected} stocks, got {actual}")
        
        # Create lookup dicts for matching
        historical_dict = {row['name']: row for row in historical_rows}
        metrics_dict = {row['name']: row for row in metrics_rows}
        
        # Process trading data and match with other tables
        for trading_row in trading_rows:
            stock_name = trading_row['name']
            t = trading_row['data']
            href = trading_row['href']
            stock_list = trading_row['list']
            
            # Add list to data
            if len(t) >= 8:
                all_trading_data.append({
                    'timestamp': f'{timestamp}T{t[-1]}:00',
                    'list': stock_list,
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
            
            # Match historical data
            if stock_name in historical_dict:
                h = historical_dict[stock_name]['data']
                if len(h) >= 7:
                    t_time = t[-1] if len(t) >= 8 else '00:00'
                    all_historical_data.append({
                        'timestamp': f'{timestamp}T{t_time}:00',
                        'list': stock_list,
                        'name': h[0],
                        'year_high': clean_number(h[1]),
                        'date_year_high': clean_number(h[2]),
                        'change_1d': clean_number(h[3]),
                        'change_1m': clean_number(h[4]),
                        'change_in_y': clean_number(h[5]),
                        'change_1y': clean_number(h[6])
                    })
            
            # Match metrics data
            if stock_name in metrics_dict:
                m = metrics_dict[stock_name]['data']
                if len(m) >= 7:
                    t_time = t[-1] if len(t) >= 8 else '00:00'
                    all_metrics_data.append({
                        'timestamp': f'{timestamp}T{t_time}:00',
                        'list': stock_list,
                        'name': m[0],
                        'pe_ratio': clean_number(m[1]),
                        'ps_ratio': clean_number(m[2]),
                        'earning_per_share': clean_number(m[3]),
                        'equity_per_share': clean_number(m[4]),
                        'dividend_yield': clean_number(m[5]),
                        'direct_return': clean_number(m[6])
                    })
    
    # Count stocks per list in final data
    print(f"\n{'='*60}")
    print("📊 Final Data Summary by List:")
    print(f"{'='*60}")
    
    from collections import Counter
    trading_counts = Counter(row['list'] for row in all_trading_data)
    for list_name, count in trading_counts.items():
        expected = expected_counts.get(list_name, 0)
        status = "✅" if count == expected else "⚠️"
        # print(f"  {status} {list_name}: {count} stocks (expected: {expected})")
    
    print(f"\nTotal stocks: {len(all_trading_data)}")
    print(f"Expected total: {sum(expected_counts.values())}")
    print(f"{'='*90}")
    
    
    # Send to API if enabled
    if API_ENABLED:
        print(f"\n{'='*90}")
        print("📤 Sending data to API...")
        print(f"{'='*90}")
        api_success = send_to_api(all_trading_data, all_historical_data, all_metrics_data)
        
        if not api_success:
            print("⚠️  API upload failed, falling back to CSV")
    else:
        print(f"\n⚠️  API disabled (API_ENABLED={API_ENABLED}), writing to CSV only")
    
    # Write CSV files (always write as backup or if API disabled)
    print(f"\n📤 Writing CSV files (backup)...")
    print(f"{'='*90}")
    
    if WRITE_TO_CSV_ENABLED:
        if all_trading_data:
            write_to_csv(CSV_OUTPUT_DIR, all_trading_data, 'all_stocks_trading.csv')
        
        if all_historical_data:
            write_to_csv(CSV_OUTPUT_DIR, all_historical_data, 'all_stocks_historical.csv')
        
        if all_metrics_data:
            write_to_csv(CSV_OUTPUT_DIR, all_metrics_data, 'all_stocks_metrics.csv')
    
    print(f"\n{'='*90}")
    print("✅ SCRAPING COMPLETE!")
    print(f"{'='*90}")

if __name__ == "__main__":
    scrape_disestockdata()