import json
import os
from datetime import datetime
from pathlib import Path

class FacebookGoldPost:
    def __init__(self, data_file="data/gold_prices.json"):
        self.data_file = data_file
        self.latest_price = None
        
    def load_latest_price(self):
        """โหลดข้อมูลราคาทองคำล่าสุด"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                prices = json.load(f)
                if prices:
                    self.latest_price = prices[-1]  # ข้อมูลล่าสุดอยู่ตำแหน่งท้ายสุด
                    return True
                else:
                    print("[ERROR] ไม่มีข้อมูลราคาทองคำ")
                    return False
        except FileNotFoundError:
            print(f"[ERROR] ไม่พบไฟล์ {self.data_file}")
            return False
        except json.JSONDecodeError:
            print(f"[ERROR] ไฟล์ {self.data_file} มีรูปแบบไม่ถูกต้อง")
            return False
    
    def format_price(self, price_str):
        """จัดรูปแบบราคา (เอาคอมม่าออก แล้วใส่กลับเป็นรูปแบบไทย)"""
        return price_str
    
    def get_trend_emoji(self, diff):
        """ดึง emoji ตามการเปลี่ยนแปลงราคา"""
        try:
            diff_value = int(diff.replace(',', ''))
            if diff_value > 0:
                return "ขึ้น"
            elif diff_value < 0:
                return "ลง"
            else:
                return "คงที่"
        except:
            return ""
    
    def get_trend_color_text(self, diff):
        """ข้อความสีสำหรับ trend"""
        try:
            diff_value = int(diff.replace(',', ''))
            if diff_value > 0:
                return "เพิ่มขึ้น"
            elif diff_value < 0:
                return "ลดลง"
            else:
                return "ไม่เปลี่ยนแปลง"
        except:
            return ""
    
    def create_post_basic(self):
        """สร้างโพสต์แบบพื้นฐาน (ข้อความอย่างเดียว)"""
        if not self.latest_price:
            return None
        
        data = self.latest_price
        trend_text_emoji = self.get_trend_emoji(data['diff'])
        trend_text_color = self.get_trend_color_text(data['diff'])
        
        post = f"""ราคาทองคำวันนี้
━━━━━━━━━━━━━━━━━━━━

อัพเดท: {data['asdate']}
ครั้งที่: {data['nqy']}

ทองคำแท่ง 96.5%
รับซื้อ: {data['blbuy']} บาท
ขาย: {data['blsell']} บาท

ทองรูปพรรณ 96.5%
รับซื้อ: {data['ombuy']} บาท
ขาย: {data['omsell']} บาท

ข้อมูลตลาดโลก
Gold Spot: ${data['goldspot']}
อัตราแลกเปลี่ยน: {data['bahtusd']} บาท/ดอลลาร์

{trend_text_emoji} การเปลี่ยนแปลง: {data['diff']} บาท
{trend_text_color}

━━━━━━━━━━━━━━━━━━━━
#ราคาทอง #ราคาทองวันนี้ #ทองคำ #GoldPrice #ทองคำแท่ง #ทองรูปพรรณ #อัพเดทราคาทอง
"""
        return post
    
    def create_post_short(self):

        """สร้างโพสต์แบบสั้น (เหมาะสำหรับ Story หรือ Quick Update)"""
        if not self.latest_price:
            return None
        
        data = self.latest_price
        trend_text_emoji = self.get_trend_emoji(data['diff'])
        
        post = f"""ราคาทองคำ {data['asdate']}

ทองแท่ง: {data['blbuy']} / {data['blsell']}
ทองรูปพรรณ: {data['ombuy']} / {data['omsell']}

{trend_text_emoji} {data['diff']} บาท

#ราคาทอง #ทองคำ
"""
        return post
    
    def create_post_detailed(self):
        """สร้างโพสต์แบบละเอียด (พร้อมคำแนะนำ)"""
        if not self.latest_price:
            return None
        
        data = self.latest_price
        trend_text_emoji = self.get_trend_emoji(data['diff'])
        trend_text_color = self.get_trend_color_text(data['diff'])
        
        # คำแนะนำตามแนวโน้ม
        try:
            diff_value = int(data['diff'].replace(',', ''))
            if diff_value > 100:
                advice = "ราคาขึ้นแรง! ผู้ถือทองอาจพิจารณาขายทำกำไร"
            elif diff_value < -100:
                advice = "ราคาลดลง! โอกาสดีสำหรับผู้ที่ต้องการสะสมทอง"
            else:
                advice = "ราคาค่อนข้างคงที่ รอจังหวะที่เหมาะสม"
        except:
            advice = "ติดตามราคาทองอย่างต่อเนื่อง"
        
        post = f"""อัพเดทราคาทองคำ
━━━━━━━━━━━━━━━━━━━━━━━━

วันที่: {data['asdate']}
อัพเดทครั้งที่: {data['nqy']} (วันนี้)

ทองคำแท่ง 96.5%
┏━━━━━━━━━━━━━━━━━━━
┃ รับซื้อ: {data['blbuy']} บาท
┃ ขายออก: {data['blsell']} บาท
┗━━━━━━━━━━━━━━━━━━━

ทองรูปพรรณ 96.5%
┏━━━━━━━━━━━━━━━━━━━
┃ รับซื้อ: {data['ombuy']} บาท
┃ ขายออก: {data['omsell']} บาท
┗━━━━━━━━━━━━━━━━━━━

ข้อมูลตลาดโลก
┏━━━━━━━━━━━━━━━━━━━
┃ Gold Spot: ${data['goldspot']}/ออนซ์
┃ USD/THB: {data['bahtusd']} บาท
┗━━━━━━━━━━━━━━━━━━━

{trend_text_emoji} การเปลี่ยนแปลง: {data['diff']} บาท
{trend_text_color}

{advice}

━━━━━━━━━━━━━━━━━━━━━━━━
ข้อมูลจาก: สมาคมค้าทองคำ
อัพเดทอัตโนมัติทุก 30 นาที

#ราคาทอง #ราคาทองวันนี้ #ทองคำ #GoldPrice 
#ทองคำแท่ง #ทองรูปพรรณ #อัพเดทราคาทอง
#ลงทุนทอง #ซื้อทอง #ขายทอง #ตลาดทอง
"""
        post += f"""

เรียนรู้เพิ่มเติมเกี่ยวกับการลงทุนในทองคำ:
ศึกษาข้อมูลเพิ่มเติมและติดตามข่าวสารราคาทองคำได้ที่ [ชื่อเว็บไซต์/เพจของคุณ] เพื่อประกอบการตัดสินใจลงทุนอย่างชาญฉลาด!
"""
        return post
    
    def create_post_with_comparison(self, compare_hours_ago=1):
        """สร้างโพสต์พร้อมเปรียบเทียบราคา"""
        if not self.latest_price:
            return None
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                prices = json.load(f)
                
            current = prices[-1]  # ข้อมูลล่าสุด
            
            # หาข้อมูลย้อนหลัง (ประมาณ 2 ครั้งต่อชั่วโมง = 2 * hours)
            compare_index = min(compare_hours_ago * 2, len(prices) - 1)
            previous = prices[compare_index]
            
            # คำนวณการเปลี่ยนแปลง
            curr_buy = float(current['blbuy'].replace(',', ''))
            prev_buy = float(previous['blbuy'].replace(',', ''))
            change = curr_buy - prev_buy
            
            trend = "เพิ่มขึ้น" if change > 0 else "ลดลง" if change < 0 else "คงที่"
            
            post = f"""สรุปราคาทองคำ
━━━━━━━━━━━━━━━━━━━━

ตอนนี้ ({current['asdate']})
ทองแท่ง: {current['blbuy']} / {current['blsell']}
ทองรูปพรรณ: {current['ombuy']} / {current['omsell']}

เมื่อ {compare_hours_ago} ชั่วโมงที่แล้ว ({previous['asdate']})
ทองแท่ง: {previous['blbuy']} / {previous['blsell']}

{trend} {abs(change):,.0f} บาท

#ราคาทอง #ทองคำ #เปรียบเทียบราคา
"""
            return post
            
        except Exception as e:
            print(f"[ERROR] เกิดข้อผิดพลาดในการเปรียบเทียบ: {e}")
            return self.create_post_basic()
    
    def save_post_to_file(self, post_text, filename="facebook_post.txt"):
        """บันทึกโพสต์ลงไฟล์"""
        try:
            output_dir = Path("out")
            output_dir.mkdir(exist_ok=True)
            
            filepath = output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(post_text)
            
            print(f"[OK] บันทึกโพสต์ไปที่: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"[ERROR] ไม่สามารถบันทึกไฟล์: {e}")
            return None
    
    def copy_to_clipboard(self, text):
        """คัดลอกข้อความไปยัง clipboard (ต้องติดตั้ง pyperclip)"""
        try:
            import pyperclip
            pyperclip.copy(text)
            print("[OK] คัดลอกโพสต์ไปยัง clipboard แล้ว!")
            return True
        except ImportError:
            print("[WARN] ต้องติดตั้ง pyperclip ก่อน: pip install pyperclip")
            return False
        except Exception as e:
            print(f"[ERROR] ไม่สามารถคัดลอก: {e}")
            return False


def main():
    """ฟังก์ชันหลัก"""
    print("=" * 50)
    print("[INFO] Facebook Gold Price Post Generator")
    print("=" * 50)
    
    # สร้าง instance
    fb_post = FacebookGoldPost()
    
    # โหลดข้อมูล
    if not fb_post.load_latest_price():
        return
    
    print("\n[INFO] เลือกรูปแบบโพสต์:")
    print("1. โพสต์แบบพื้นฐาน (Basic)")
    print("2. โพสต์แบบสั้น (Short)")
    print("3. โพสต์แบบละเอียด (Detailed)")
    print("4. โพสต์พร้อมเปรียบเทียบ (Comparison)")
    print("5. สร้างทุกรูปแบบ (All)")
    
    choice = input("\n[INPUT] เลือก (1-5): ").strip()
    
    posts = {}
    
    if choice == "1":
        posts["basic"] = fb_post.create_post_basic()
    elif choice == "2":
        posts["short"] = fb_post.create_post_short()
    elif choice == "3":
        posts["detailed"] = fb_post.create_post_detailed()
    elif choice == "4":
        posts["comparison"] = fb_post.create_post_with_comparison()
    elif choice == "5":
        posts["basic"] = fb_post.create_post_basic()
        posts["short"] = fb_post.create_post_short()
        posts["detailed"] = fb_post.create_post_detailed()
        posts["comparison"] = fb_post.create_post_with_comparison()
    else:
        print("[ERROR] ตัวเลือกไม่ถูกต้อง")
        return
    
    # แสดงและบันทึกโพสต์
    for post_type, post_text in posts.items():
        if post_text:
            print("\n" + "=" * 50)
            print(f"[INFO] โพสต์แบบ: {post_type.upper()}")
            print("=" * 50)
            print(post_text)
            
            # บันทึกลงไฟล์
            filename = f"facebook_post_{post_type}.txt"
            fb_post.save_post_to_file(post_text, filename)
    
    # ถามว่าต้องการคัดลอกไหม
    if len(posts) == 1:
        copy_choice = input("\n[INPUT] คัดลอกไปยัง clipboard? (y/n): ").strip().lower()
        if copy_choice == 'y':
            post_text = list(posts.values())[0]
            fb_post.copy_to_clipboard(post_text)
    
    print("\n[OK] เสร็จสิ้น!")


if __name__ == "__main__":
    main()