import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# ฟังก์ชันสำหรับคืนค่าเวลาปัจจุบันในรูปแบบ string
def xnowtime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ฟังก์ชันบันทึกข้อมูลเป็น JSON ไฟล์
def save_to_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ฟังก์ชันดึงข้อมูลราคาทองคำจากเว็บไซต์
def scrape_gold_data(url='https://www.goldtraders.or.th/UpdatePriceList.aspx'):
    try:
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, 'html.parser')

        table = soup.find("table", {"id": "DetailPlace_MainGridView"})
        if not table:
            return []

        data = []
        for row in table.find_all("tr")[1:]:  # ข้ามหัวตาราง
            cols = row.find_all("td")
            if len(cols) == 9:
                data.append({
                    'asdate': cols[0].get_text(strip=True),
                    'nqy': cols[1].get_text(strip=True),
                    'blbuy': cols[2].get_text(strip=True),
                    'blsell': cols[3].get_text(strip=True),
                    'ombuy': cols[4].get_text(strip=True),
                    'omsell': cols[5].get_text(strip=True),
                    'goldspot': cols[6].get_text(strip=True),
                    'bahtusd': cols[7].get_text(strip=True),
                    'diff': cols[8].get_text(strip=True),
                })
        return data[::-1]  # กลับลำดับล่าสุดไปเก่าสุด
    except Exception as e:
        print(f"[{xnowtime()}] Error while scraping: {e}")
        return []

# ฟังก์ชันสำหรับทดสอบ GET API (ไม่จำเป็นเท่าไหร่ถ้าไม่มีการใช้งานผลลัพธ์)
def send_api():
    try:
        res = requests.get('https://karndiy.pythonanywhere.com/cjson/goldjson-v2', timeout=5)
        print(f"[{xnowtime()}] API GET status: {res.status_code}")
    except Exception as e:
        print(f"[{xnowtime()}] Error during GET request: {e}")

# ฟังก์ชันหลักสำหรับดึงข้อมูลราคาทอง และส่ง POST ไปยัง API
def cjson_pythonanywhere():
    url = 'https://karndiy.pythonanywhere.com/cjson/goldjson-v2'
    data = scrape_gold_data()

    if not data:
        print("No data scraped, aborting POST request.")
        return "No data scraped."

    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 201:
            save_to_json(data, "data/gold_prices.json")
          
            print(f"{data}")
            return response.json()
        else:
            print("Error creating JSON file:", response.text)
            return response.json()
    except Exception as e:
        print(f"[{xnowtime()}] Error during POST request: {e}")
        return str(e)
    
if __name__ == "__main__":
    cjson_pythonanywhere()
