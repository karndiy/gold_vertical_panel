import requests
import json
import os
import sys

CONFIG_FILE = "config.json"
GOLD_DATA_FILE = "data/gold_prices.json"

def load_config():
    """Load configuration from JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        return None
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {CONFIG_FILE}: {e}")
        return None

def load_latest_gold_price():
    """Load the latest gold price from data/gold_prices.json."""
    if not os.path.exists(GOLD_DATA_FILE):
        print(f"Error: {GOLD_DATA_FILE} not found.")
        return None
    
    try:
        with open(GOLD_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                # Return the last entry (latest)
                return data[-1]
            else:
                print("Error: No data found in gold_prices.json")
                return None
    except Exception as e:
        print(f"Error reading {GOLD_DATA_FILE}: {e}")
        return None

def format_gold_message(gold_data):
    """Format gold price data into a readable message."""
    asdate = gold_data.get("asdate", "-")
    nqy = gold_data.get("nqy", "-")
    blbuy = gold_data.get("blbuy", "-")
    blsell = gold_data.get("blsell", "-")
    ombuy = gold_data.get("ombuy", "-")
    omsell = gold_data.get("omsell", "-")
    diff = gold_data.get("diff", "-")
    goldspot = gold_data.get("goldspot", "-")
    bahtusd = gold_data.get("bahtusd", "-")
    
    # Determine trend emoji
    if diff.startswith("-"):
        trend = "📉 ลง"
    elif diff.startswith("+"):
        trend = "📈 ขึ้น"
    else:
        trend = "➡️ คงที่"
    
    message = f"""🏆 ราคาทองคำล่าสุด

📅 วันที่: {asdate}
🔢 ครั้งที่: {nqy}

💰 ทองคำแท่ง 96.5%
├ รับซื้อ: {blbuy} บาท
└ ขายออก: {blsell} บาท

💍 ทองรูปพรรณ
├ รับซื้อ: {ombuy} บาท
└ ขายออก: {omsell} บาท

{trend} การเปลี่ยนแปลง: {diff} บาท

🌍 Gold Spot: ${goldspot}
💵 USD/THB: {bahtusd}

━━━━━━━━━━━━━━━━
ข้อมูลจาก: สมาคมค้าทองคำ"""
    
    return message

def send_telegram_message(message):
    """Send a text message to Telegram."""
    config = load_config()
    if not config: return False

    token = config.get("telegram_bot_token")
    chat_id = config.get("telegram_chat_id")

    if not token or not chat_id or "YOUR_" in token:
        print("Error: Please set 'telegram_bot_token' and 'telegram_chat_id' in config.json")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[OK] Message sent successfully!")
            return True
        else:
            print(f"[ERROR] Failed to send message: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error sending message: {e}")
        return False

def send_telegram_video(video_path, caption=""):
    """Send a video file to Telegram."""
    config = load_config()
    if not config: return False

    token = config.get("telegram_bot_token")
    chat_id = config.get("telegram_chat_id")

    if not token or not chat_id or "YOUR_" in token:
        print("Error: Please set 'telegram_bot_token' and 'telegram_chat_id' in config.json")
        return False

    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return False

    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    try:
        with open(video_path, "rb") as video_file:
            files = {"video": video_file}
            data = {"chat_id": chat_id, "caption": caption}
            
            print(f"Sending video: {video_path}...")
            response = requests.post(url, data=data, files=files, timeout=60)
            
            if response.status_code == 200:
                print("[OK] Video sent successfully!")
                return True
            else:
                print(f"[ERROR] Failed to send video: {response.text}")
                return False
    except Exception as e:
        print(f"[ERROR] Error sending video: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  TELEGRAM GOLD PRICE NOTIFIER")
    print("="*60 + "\n")
    
    # Load latest gold price
    gold_data = load_latest_gold_price()
    
    if gold_data:
        # Format message
        message = format_gold_message(gold_data)
        print("Message prepared (contains emoji, not displayed in console)")
        print("="*60 + "\n")
        
        # Send message
        if send_telegram_message(message):
            print("\nGold price update sent to Telegram!")
        
        # Auto-send video if exists (no user prompt for automation)
        video_path = "out/output.mp4"
        if os.path.exists(video_path):
            print(f"\nFound video file: {video_path}")
            print("Sending video automatically...")
            send_telegram_video(video_path, f"🎬 ราคาทองคำ ครั้งที่ {gold_data.get('nqy', '-')}")
        else:
            print(f"\nVideo not found at {video_path}, skipping video.")
    else:
        print("Cannot load gold price data. Please run getgold.py first.")
        sys.exit(1)



