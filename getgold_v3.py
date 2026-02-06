import json
import time
import requests
import sys
from datetime import datetime
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
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

def get_gold_price_data():
    """Scrapes gold prices using Playwright based on the new GTA layout."""
    url = "https://www.goldtraders.or.th/updatepricelist"
    print(f"[{xnowtime()}] Connecting to {url} ...")
    
    # Get today's date for the 'asdate' field since the table only shows Time
    today_str = datetime.now().strftime("%d/%m/%Y")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=60000)
            # Wait for the specific history body ID
            page.wait_for_selector("#history-body", timeout=30000)
            time.sleep(2) 
            html_content = page.content()
        except Exception as e:
            print(f"Error during scraping: {e}")
            browser.close()
            return []
            
        browser.close()

    soup = BeautifulSoup(html_content, 'html.parser')
    # Target the specific tbody from your snippet
    tbody = soup.find('tbody', id='history-body')
    
    if not tbody:
        print("Table body #history-body not found!")
        return []

    data_list = []
    rows = tbody.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        
        # New structure has 9 columns: 
        # 0:No, 1:Time, 2:BarSell, 3:BarBuy, 4:JewelSell, 5:JewelBuy, 6:Spot, 7:THB, 8:Change
        if len(cols) >= 9:
            txt = [c.get_text(strip=True) for c in cols]
            
            # Formatting asdate using Today + Scraped Time
            asdate_val = f"{today_str} {txt[1]}"
            clean_diff = txt[8].replace('Change ', '').replace('change ', '').strip()
            
            item = {
                "asdate": asdate_val,
                "nqy": txt[0],      # Round number (ครั้งที่)
                "ombuy": txt[3],    # Gold Bar Buy (แท่ง รับซื้อ)
                "omsell": txt[2],   # Gold Bar Sell (แท่ง ขายออก)
                "blbuy": txt[5],    # Jewelry Buy (รูปพรรณ รับซื้อ)
                "blsell": txt[4],   # Jewelry Sell (รูปพรรณ ขายออก)
                "goldspot": txt[6], # Gold Spot
                "bahtusd": txt[7],  # THB/USD
                "diff": clean_diff #txt[8]      # Change (เปลี่ยนแปลง)
            }
            data_list.append(item)

    return data_list

def save_and_sort_json(data, filename):
    """Sorts data by time and saves to JSON file."""
    try:
        # Sort so that the latest update (higher round number) is first or last
        # Currently sorting by time string
        data.sort(
            key=lambda x: datetime.strptime(x['asdate'], '%d/%m/%Y %H:%M'),
            reverse=True # Latest first
        )
        print("✅ Data sorted by Time (Latest First)")
    except Exception as e:
        print(f"⚠️ Warning: Could not sort data ({e}).")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully exported {len(data)} items to '{filename}'")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    gold_data = get_gold_price_data()
    
    if gold_data:
        save_and_sort_json(gold_data, OUTPUT_FILE)
        
        print(f"[{xnowtime()}] Posting {len(gold_data)} items to server...")
        status, body = post_data(POST_URL, gold_data)
        
        if status in [200, 201]:
            print(f"[{xnowtime()}] POST OK {status}")
            sys.exit(0)
        elif status is None:
            print(f"[{xnowtime()}] POST failed: {body}")
            sys.exit(3)
        else:
            print(f"[{xnowtime()}] POST error: HTTP {status} - {body[:200]}")
            sys.exit(4)
    else:
        print(f"[{xnowtime()}] No data extracted.")
        sys.exit(1)