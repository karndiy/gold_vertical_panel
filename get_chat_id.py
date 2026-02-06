import requests
import json

# ใส่ Token ที่คุณมี
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # แทนที่ด้วย token ของคุณ

print("กำลังดึงข้อมูลการสนทนาล่าสุด...")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data.get("ok") and data.get("result"):
        print("\n✅ พบการสนทนาล่าสุด:\n")
        for update in data["result"][-3:]:  # แสดง 3 ล่าสุด
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                from_user = update["message"]["from"].get("first_name", "Unknown")
                text = update["message"].get("text", "(no text)")
                print(f"Chat ID: {chat_id}")
                print(f"From: {from_user}")
                print(f"Message: {text}")
                print("-" * 50)
    else:
        print("❌ ยังไม่มีข้อความในบอท")
        print("กรุณาส่งข้อความใดก็ได้ไปที่ @karndevbot ก่อน แล้วรันสคริปต์นี้อีกครั้ง")
        
except Exception as e:
    print(f"Error: {e}")
