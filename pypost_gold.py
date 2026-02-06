import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# การตั้งค่าพื้นฐาน
SCOPES = ['https://www.googleapis.com/auth/blogger']
TARGET_BLOG_ID = "8971911068975230651"  # บล็อกราคาทองคำของคุณ
JSON_FILE_PATH = r"E:\gold_vertical_panel\data\gold_prices.json"

def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('blogger', 'v3', credentials=creds)

def post_to_blogger(service, blog_id, title, content, labels=[]):
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": labels
    }
    try:
        request = service.posts().insert(blogId=blog_id, body=body)
        response = request.execute()
        print(f"[OK] Post published successfully! URL: {response.get('url')}")
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")

def run_auto_post():
    # 1. อ่านข้อมูลล่าสุดจาก JSON
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # ดึงข้อมูลตัวสุดท้ายในลิสต์ (ล่าสุด)
            latest = data[-1]
    except Exception as e:
        print(f"[ERROR] Cannot read JSON file: {e}")
        return

    # 2. เตรียมข้อมูลสำหรับโพสต์
    update_time = latest['asdate']
    buy_price = latest['blbuy']
    sell_price = latest['blsell']
    diff_val = latest['diff']
    
    # ใส่สัญลักษณ์ บวก/ลบ
    prefix = "+" if not diff_val.startswith("-") and diff_val != "0" else ""
    status_icon = "▲" if prefix == "+" else "▼" if diff_val.startswith("-") else "●"

    title = f"ราคาทองคำวันนี้ อัปเดตครั้งที่ {latest['nqy']} ({update_time}) [ {prefix}{diff_val} ]"
    
    content = f"""
    <div style="font-family: 'Helvetica', sans-serif; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
        <h2 style="color: #d4af37;">รายงานราคาทองคำล่าสุด</h2>
        <p><b>ประจำวันที่:</b>  {latest['nqy']}  {update_time}</p>
        <hr>
        <table style="width: 100%; text-align: left;">
            <tr>
                <td><b>ทองแท่งรับซื้อ:</b></td>
                <td style="color: green; font-size: 1.2em;"><b>{buy_price} บาท</b></td>
            </tr>
            <tr>
                <td><b>ทองแท่งขายออก:</b></td>
                <td style="color: red; font-size: 1.2em;"><b>{sell_price} บาท</b></td>
            </tr>
            <tr>
                <td><b>การเปลี่ยนแปลง:</b></td>
                <td><b style="color: {'green' if prefix == '+' else 'red'};">{status_icon} {prefix}{diff_val} บาท</b></td>
            </tr>
        </table>
        <br>
        <p style="font-size: 0.9em; color: #666;">
            Gold Spot: {latest['goldspot']} | ค่าเงินบาท: {latest['bahtusd']}
        </p>
    </div>
    """
    
    # 3. ส่งข้อมูลไป Blogger
    service = get_service()
    post_to_blogger(service, TARGET_BLOG_ID, title, content, ["ราคาทองคำ", "ข่าวทอง","goldprice","ทองคำ"])

if __name__ == '__main__':
    run_auto_post()