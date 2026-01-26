import json
import time
import requests
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Try to import xnowtime from your local 'getgold.py', otherwise use a fallback
try:
    from getgold import xnowtime
except ImportError:
    def xnowtime():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- CONFIGURATION ---
POST_URL = 'https://karndiy.pythonanywhere.com/cjson/goldjson-v2'
OUTPUT_FILE = "gold_prices.json"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "GoldScraper/1.0"
}

def post_data(url: str, payload: list):
    """Sends the scraped data to the remote server."""
    try:
        # payload is the list of dicts directly
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

def get_gold_price_data():
    """Scrapes gold prices using Playwright."""
    url = "https://www.goldtraders.or.th/updatepricelist"
    print(f"[{xnowtime()}] Connecting to {url} ...")
    
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. Visit URL
            page.goto(url, timeout=60000)
            
            # 2. Wait for table
            # print("Waiting for table data...")
            page.wait_for_selector("table", timeout=30000)
            time.sleep(3) # Extra wait for rendering
            
            # 3. Get HTML
            html_content = page.content()
            
        except Exception as e:
            browser.close()
            print(f"Error during scraping: {e}")
            return []
            
        browser.close()

    # 4. Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    if not table:
        print("Table not found!")
        return []

    data_list = []
    rows = table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        
        # Ensure enough columns (9+)
        if len(cols) >= 9:
            txt = [c.get_text(strip=True) for c in cols]
            
            # Check if first col is Date
            if '/' not in txt[0]:
                continue
            
            item = {
                "asdate": f"{txt[0]} {txt[1]}",
                "nqy": txt[2],
                "ombuy": txt[3],
                "omsell": txt[4],
                "blbuy": txt[5],
                "blsell": txt[6],
                "goldspot": txt[7],
                "bahtusd": txt[8],
                "diff": txt[9]
            }
            data_list.append(item)

    return data_list

def save_and_sort_json(data, filename):
    """Sorts data by date and saves to JSON file."""
    # --- SORTING LOGIC ---
    try:
        # Sort by Date string parsing
        data.sort(
            key=lambda x: datetime.strptime(x['asdate'], '%d/%m/%Y %H:%M')
            # Add reverse=True here if you want Latest First
        )
        print("✅ Data sorted by Time")
    except Exception as e:
        print(f"⚠️ Warning: Could not sort data ({e}). Saving unsorted.")

    # Save to file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully exported {len(data)} items to '{filename}'")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    # 1. Scrape Data
    gold_data = get_gold_price_data()
    
    if gold_data:
        # 2. Save & Sort
        save_and_sort_json(gold_data, OUTPUT_FILE)
        
        # 3. Post Data
        print(f"[{xnowtime()}] Posting {len(gold_data)} items to server...")
        status, body = post_data(POST_URL, gold_data)
        
        # Check HTTP Status Code
        if status == 201 or status == 200:
            print(f"[{xnowtime()}] POST OK {status}")
            # print(gold_data) # Uncomment to see data in console
            sys.exit(0) # Exit with Success Code
            
        elif status is None:
            print(f"[{xnowtime()}] POST failed (Connection Error): {body}")
            sys.exit(3) # Exit with Network Error Code
            
        else:
            print(f"[{xnowtime()}] POST error: HTTP {status} - {body[:300]}...")
            sys.exit(4) # Exit with HTTP Error Code
            
    else:
        print(f"[{xnowtime()}] No data extracted.")
        sys.exit(1) # Exit with No Data Code