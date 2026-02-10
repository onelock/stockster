import asyncio
from playwright.async_api import async_playwright
import datetime
import os
import csv
from urllib.parse import urljoin
import requests
import re

CSV_OUTPUT_DIR = os.getenv('CSV_OUTPUT_DIR', '/data')
BASE_URL = "https://www.di.se/bors/aktier/"
API_URL = os.getenv('API_URL', 'http://localhost:8000/api/v1')
API_ENABLED = os.getenv('API_ENABLED', 'true').lower() == 'true'
WRITE_TO_CSV_ENABLED=os.getenv('WRITE_TO_CSV_ENABLED', 'true').lower() == 'true'

FLOAT_CLEANING_REGEX = re.compile(r'[,\s\xa0%]|kr')
INTEGER_CLEANING_REGEX = re.compile(r'[,\s\xa0]')
FLOAT_CLEANING_LAMBDA = lambda m: '.' if m.group() == ',' else ''

MARKET_LIST_LIMIT = 5
CONCURRENT_SCRAPE_LIMIT = 5

def clean_number(s):
    if s is None: return None
    try:
        cleaned = FLOAT_CLEANING_REGEX.sub(FLOAT_CLEANING_LAMBDA, s)
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def clean_integer(s):
    if s is None: return None
    try:
        cleaned = INTEGER_CLEANING_REGEX.sub('', s)
        return int(cleaned)
    except (ValueError, TypeError):
        return None
    
    
def build_file_path(file_type: str, extension: str = "csv") -> str:
    """Build file path for output files"""
    now = datetime.datetime.now() 
    
    year = now.strftime("%Y") 
    month = now.strftime("%m") 
    day = now.strftime("%d") 
    
    folder_path = os.path.join(CSV_OUTPUT_DIR, year, month, day)
    os.makedirs(folder_path, exist_ok=True)
    filename = f"{file_type}.{extension}"
    
    return os.path.join(folder_path, filename)


def write_to_csv(data, filename, mode='a'):
    """Write data to CSV file"""
    csv_file = build_file_path(filename)
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

async def scrape_page_optimized(browser, item):
    """ Scrape a single list page concurrently with resource blocking """
    context = await browser.new_context()
    page = await context.new_page()
    
    # Block unnecessary resources
    await page.route("**/*.{png,jpg,jpeg,svg,gif,css,woff,woff2}", lambda route: route.abort())
    
    try:
        await page.goto(item['href'], wait_until="domcontentloaded")  # noqa: SC200
        await page.wait_for_timeout(2000)  # Wait for initial content
            
        data = await page.evaluate("""
            async () => {
                const delay = ms => new Promise(res => setTimeout(res, ms));
                let lastCount = 0;
                let retries = 0;
                let scrollAttempts = 0;
                const maxScrollAttempts = 100;
                
                // Keep scrolling until no new rows appear for 8 consecutive attempts
                while (retries < 8 && scrollAttempts < maxScrollAttempts) {
                    window.scrollTo(0, document.body.scrollHeight);
                    await delay(500);
                    
                    // Also scroll to last row to trigger lazy load
                    const lastRow = document.querySelector('table[data-tab="table_0"] tbody tr:last-child');
                    if (lastRow) lastRow.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    await delay(500);
                    
                    let currentCount = document.querySelectorAll('table[data-tab="table_0"] tbody tr').length;
                    scrollAttempts++;
                    
                    if (currentCount == lastCount) retries++;
                    else { 
                        console.log(`Scroll ${scrollAttempts}: ${currentCount} rows (+${currentCount - lastCount})`);
                        lastCount = currentCount; 
                        retries = 0; 
                    }
                }
                
                const extract = (tabId) => { 
                    return Array.from(document.querySelectorAll(`table[data-tab="${tabId}"] tbody tr`)).map(row => {
                        const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim());
                        const link = row.querySelector('a');
                        return {
                            name: cells[0],
                            data: cells,
                            href: link ? link.getAttribute('href') : null,
                        };
                    });
                };
                return {
                    table_0: extract('table_0'),
                    table_1: extract('table_1'),
                    table_2: extract('table_2'),
                };
            }
        """)
    
        await context.close()
        return {item['text']: {'data': data, 'list': item['text']}}
    except Exception as e:
        print(f"  ❌ Error scraping {item['text']}: {e}")
        await context.close()
        return {}


def process_and_send(all_pages_data):
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d')
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
    
    # Combine data from all pages
    all_trading = []
    all_historical = []
    all_metrics = []
    
    
    for list_name, info in all_pages_data.items():
        data = info['data']
        
        hist_lookup = {row['name']: row for row in data.get('table_1', [])}
        metr_lookup = {row['name']: row for row in data.get('table_2', [])}
        
        
        seen = set()
        for stock in data.get('table_0', []):
            if stock['name'] in seen:
                continue
            
            seen.add(stock['name'])
            
            name =  stock['name']
            t = stock['data']
            href = stock['href']
            
            t_time = t[-1] if len(t) >= 8 else '00:00'
            iso_ts = f'{timestamp}T{t_time}:00'
            
            # Add list to data
            if len(t) >= 8:
                all_trading.append({
                    'timestamp': iso_ts,
                    'list': list_name,
                    'name': name,
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
            h = hist_lookup.get(name)
            h_data = h['data'] if h else []
            if len(h_data) >= 8:
                all_historical.append({
                    'timestamp': iso_ts,
                    'list': list_name,
                    'name': name,
                    'ath': clean_number(h_data[2]),
                    'date_of_ath': h_data[3],
                    'one_day_change': clean_number(h_data[4]),
                    'one_month_change': clean_number(h_data[5]),
                    'year_to_date_change': clean_number(h_data[6]),
                    'one_year_change': clean_number(h_data[7])
                })
            
            # Match metrics data
            m = metr_lookup.get(name)
            m_data = m['data'] if m else []
            if len(m_data) >= 8:
                all_metrics.append({
                    'timestamp': iso_ts,
                    'list': list_name,
                    'name': name,
                    'pe_ratio': clean_number(m_data[2]),
                    'ps_ratio': clean_number(m_data[3]),
                    'earning_per_share': clean_number(m_data[4]),
                    'equity_per_share': clean_number(m_data[5]),
                    'dividend_yield': clean_number(m_data[6]),
                    'direct_return': clean_number(m_data[7])
                })
                
    # Send to API if enabled
    if API_ENABLED and all_trading:
        api_success = send_to_api(all_trading, all_historical, all_metrics)
        
        if not api_success:
            print("⚠️  API upload failed, falling back to CSV")
    else:
        print(f"\n⚠️  API disabled (API_ENABLED={API_ENABLED}), writing to CSV only")
    
    # Write CSV files (always write as backup or if API disabled)
    print(f"\n📤 Writing CSV files (backup)...")
    print(f"{'='*90}")
    
    if WRITE_TO_CSV_ENABLED:
        file_ts = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        
        if all_trading: write_to_csv(all_trading, f'trading_{file_ts}')
        
        if all_historical: write_to_csv(all_historical, f'historical_{file_ts}')
        
        if all_metrics: write_to_csv(all_metrics, f'metrics_{file_ts}')
            
    print(f"✅ Processed {len(all_trading)} total stocks across {len(all_pages_data)} lists.")
    

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"📡 Navigating to {BASE_URL}...")
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        
        submenu = await page.query_selector('[aria-label="Undermeny"]')
        links = await submenu.query_selector_all("a")
        
        # Extract link info before clicking - use inner text as list name
        menu_items = []
        for link in links[:MARKET_LIST_LIMIT]:
            text = await link.inner_text()
            href = await link.get_attribute("href")
            menu_items.append({'text': text.strip(),'href': urljoin(BASE_URL, href)})
            
        print(f"🚀 Starting parallel scrape of {len(menu_items)} list...")
        sem = asyncio.Semaphore(CONCURRENT_SCRAPE_LIMIT)  # Limit concurrency
        
        async def throttled_scrape(item):
            async with sem:
                return await scrape_page_optimized(browser, item)
            
        tasks = [throttled_scrape(item) for item in menu_items]
        results = await asyncio.gather(*tasks)
        
        await browser.close()
        
        all_pages_data = {k: v for d in results for k, v in d.items()}
        process_and_send(all_pages_data)

if __name__ == "__main__":
    import time
    st = time.time()
    asyncio.run(main())
    print(f"⏱️  Total runtime: {time.time() - st:.2f} seconds")