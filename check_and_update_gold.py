"""
ตรวจสอบและอัปเดตข้อมูลราคาทองคำ
Check if gold price data is up-to-date and update if needed
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def check_data_freshness(data_file="data/gold_prices.json", max_age_minutes=60):
    """
    ตรวจสอบว่าข้อมูลล่าสุดเก่าเกินกำหนดหรือไม่
    
    Args:
        data_file: ไฟล์ข้อมูล JSON
        max_age_minutes: อายุข้อมูลสูงสุดที่ยอมรับได้ (นาที)
    
    Returns:
        tuple: (is_fresh, latest_time, age_minutes, message)
    """
    try:
        # อ่านไฟล์ JSON
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            return False, None, None, "❌ ไม่มีข้อมูลในไฟล์"
        
        # ดึงข้อมูลล่าสุด (อันแรกในลิสต์)
        latest = data[0]
        latest_time_str = latest.get('asdate_iso') or latest.get('asdate')
        
        # แปลงเป็น datetime
        try:
            if 'asdate_iso' in latest:
                latest_time = datetime.strptime(latest_time_str, '%Y-%m-%d %H:%M:%S')
            else:
                # Format: "06/02/2569 10:33"
                latest_time = datetime.strptime(latest_time_str, '%d/%m/%Y %H:%M')
        except Exception as e:
            return False, latest_time_str, None, f"❌ ไม่สามารถแปลงเวลาได้: {e}"
        
        # คำนวณอายุข้อมูล
        now = datetime.now()
        age = now - latest_time
        age_minutes = age.total_seconds() / 60
        
        # ตรวจสอบความสด
        is_fresh = age_minutes <= max_age_minutes
        
        if is_fresh:
            message = f"✅ ข้อมูลสด (อายุ {age_minutes:.0f} นาที)"
        else:
            message = f"⚠️ ข้อมูลเก่า (อายุ {age_minutes:.0f} นาที / {age_minutes/60:.1f} ชั่วโมง)"
        
        return is_fresh, latest_time, age_minutes, message
    
    except FileNotFoundError:
        return False, None, None, f"❌ ไม่พบไฟล์ {data_file}"
    except json.JSONDecodeError:
        return False, None, None, f"❌ ไฟล์ {data_file} มีรูปแบบไม่ถูกต้อง"
    except Exception as e:
        return False, None, None, f"❌ เกิดข้อผิดพลาด: {e}"


def update_gold_data():
    """รันสคริปต์ดึงข้อมูลทองคำใหม่"""
    try:
        print("\n🔄 กำลังดึงข้อมูลราคาทองคำใหม่...")
        result = subprocess.run(
            ['python', 'getgold.py'],
            capture_output=True,
            text=True,
            timeout=120  # timeout 2 นาที
        )
        
        if result.returncode == 0:
            print("✅ ดึงข้อมูลสำเร็จ!")
            print(result.stdout)
            return True
        else:
            print(f"❌ ดึงข้อมูลไม่สำเร็จ (exit code: {result.returncode})")
            print(result.stderr)
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ ดึงข้อมูลใช้เวลานานเกินไป (timeout)")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False


def main():
    """ฟังก์ชันหลัก"""
    print("=" * 70)
    print("🔍 ตรวจสอบข้อมูลราคาทองคำ")
    print("=" * 70)
    
    # ตรวจสอบความสดของข้อมูล
    is_fresh, latest_time, age_minutes, message = check_data_freshness(
        max_age_minutes=60  # ถ้าข้อมูลเก่ากว่า 60 นาที ถือว่าเก่า
    )
    
    print(f"\n📊 สถานะข้อมูล:")
    print(f"   {message}")
    
    if latest_time:
        print(f"   📅 เวลาล่าสุด: {latest_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   ⏰ ตอนนี้: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # ถามว่าต้องการอัปเดตหรือไม่
    if not is_fresh:
        print("\n" + "=" * 70)
        choice = input("❓ ต้องการดึงข้อมูลใหม่หรือไม่? (y/n): ").strip().lower()
        
        if choice == 'y':
            success = update_gold_data()
            
            if success:
                # ตรวจสอบอีกครั้งหลังอัปเดต
                print("\n" + "=" * 70)
                print("🔍 ตรวจสอบข้อมูลหลังอัปเดต:")
                is_fresh2, latest_time2, age_minutes2, message2 = check_data_freshness()
                print(f"   {message2}")
                if latest_time2:
                    print(f"   📅 เวลาล่าสุด: {latest_time2.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            print("⏭️ ข้ามการอัปเดต")
    else:
        print("\n✅ ข้อมูลยังใหม่อยู่ ไม่จำเป็นต้องอัปเดต")
    
    print("\n" + "=" * 70)
    print("✅ เสร็จสิ้น!")
    print("=" * 70)


if __name__ == "__main__":
    main()
