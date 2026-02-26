"""
Facebook Image Post Generator
สร้างรูปภาพสวยๆ สำหรับโพสต์ราคาทองคำบน Facebook
"""

import json
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime

class FacebookImageGenerator:
    def __init__(self, data_file="data/gold_prices.json"):
        self.data_file = data_file
        self.latest_price = None
        self.output_dir = Path("out")
        self.output_dir.mkdir(exist_ok=True)
        
        # ขนาดรูปภาพ (Facebook Post: 1200x630 แนะนำ)
        self.width = 1200
        self.height = 630
        
    def load_latest_price(self):
        """โหลดข้อมูลราคาทองคำล่าสุด"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                prices = json.load(f)
                if prices:
                    self.latest_price = prices[-1]  # ข้อมูลล่าสุดอยู่ตำแหน่งท้ายสุด
                    return True
                else:
                    print("❌ ไม่มีข้อมูลราคาทองคำ")
                    return False
        except FileNotFoundError:
            print(f"❌ ไม่พบไฟล์ {self.data_file}")
            return False
        except json.JSONDecodeError:
            print(f"❌ ไฟล์ {self.data_file} มีรูปแบบไม่ถูกต้อง")
            return False
    
    def get_font(self, size, bold=False):
        """ดึง font ไทยที่รองรับภาษาไทยได้ดี"""
        try:
            # ลำดับความสำคัญของ font ไทย
            if bold:
                font_paths = [
                    "C:/Windows/Fonts/tahomabd.ttf",  # Tahoma Bold - รองรับไทยดี
                    "C:/Windows/Fonts/THSarabunNew Bold.ttf",
                    "C:/Windows/Fonts/arialbd.ttf",
                    "C:/Windows/Fonts/Angsana.ttc",
                ]
            else:
                font_paths = [
                    "C:/Windows/Fonts/tahoma.ttf",  # Tahoma - รองรับไทยดีที่สุด
                    "C:/Windows/Fonts/THSarabunNew.ttf",
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/Angsana.ttc",
                ]
            
            for font_path in font_paths:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            
            # ถ้าไม่มี font ไทย แจ้งเตือน
            print(f"⚠️ ไม่พบ font ไทย กำลังใช้ font default")
            return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
            
        except Exception as e:
            print(f"❌ ไม่สามารถโหลด font: {e}")
            print("💡 กรุณาติดตั้ง Tahoma font หรือ Arial font")
            # ใช้ font default ของระบบ
            return ImageFont.load_default()
    
    def create_gradient_background(self, color1, color2):
        """สร้างพื้นหลังแบบ gradient"""
        base = Image.new('RGB', (self.width, self.height), color1)
        top = Image.new('RGB', (self.width, self.height), color2)
        mask = Image.new('L', (self.width, self.height))
        mask_data = []
        for y in range(self.height):
            mask_data.extend([int(255 * (y / self.height))] * self.width)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base
    
    def create_gold_price_image_modern(self):
        """สร้างรูปภาพแบบโมเดิร์น - ปรับปรุงใหม่"""
        if not self.latest_price:
            return None
        
        data = self.latest_price
        
        # สร้างพื้นหลัง gradient (ทอง)
        img = self.create_gradient_background(
            (255, 215, 0),   # Gold
            (218, 165, 32)   # Goldenrod
        )
        
        draw = ImageDraw.Draw(img)
        
        # Fonts - ปรับขนาดให้พอดีกับพื้นที่
        font_title = self.get_font(70, bold=True)
        font_large = self.get_font(50, bold=True)
        font_medium = self.get_font(42, bold=False)
        font_small = self.get_font(34, bold=False)
        
        # วาดกรอบขาว
        margin = 30
        draw.rectangle(
            [(margin, margin), (self.width - margin, self.height - margin)],
            outline=(255, 255, 255),
            width=6
        )
        
        # หัวข้อ - ใช้ข้อความไทยล้วน
        y_pos = 65
        title = "ราคาทองคำวันนี้"
        # วัดความกว้างของข้อความ
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((self.width - title_width) / 2, y_pos),
            title,
            fill=(255, 255, 255),
            font=font_title,
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )
        
        # วันที่และเวลา
        y_pos = 155
        date_text = f"อัปเดต: {data['asdate']}"
        date_bbox = draw.textbbox((0, 0), date_text, font=font_small)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(
            ((self.width - date_width) / 2, y_pos),
            date_text,
            fill=(255, 255, 255),
            font=font_small
        )
        
        # เส้นแบ่ง
        y_pos = 210
        draw.line([(80, y_pos), (self.width - 80, y_pos)], fill=(255, 255, 255), width=2)
        
        # ทองคำแท่ง (ซ้าย)
        y_pos = 245
        x_left = 90
        draw.text((x_left, y_pos), "ทองคำแท่ง 96.5%", fill=(255, 255, 255), font=font_large, stroke_width=2, stroke_fill=(0, 0, 0))
        
        y_pos += 60
        draw.text((x_left + 15, y_pos), f"รับซื้อ", fill=(255, 255, 255), font=font_medium)
        draw.text((x_left + 160, y_pos), f"{data['blbuy']}", fill=(255, 255, 255), font=font_medium, stroke_width=2, stroke_fill=(0, 0, 0))
        
        y_pos += 55
        draw.text((x_left + 15, y_pos), f"ขาย", fill=(255, 255, 255), font=font_medium)
        draw.text((x_left + 160, y_pos), f"{data['blsell']}", fill=(255, 255, 255), font=font_medium, stroke_width=2, stroke_fill=(0, 0, 0))
        
        # ทองรูปพรรณ (ขวา)
        y_pos = 245
        x_right = 630
        draw.text((x_right, y_pos), "ทองรูปพรรณ 96.5%", fill=(255, 255, 255), font=font_large, stroke_width=2, stroke_fill=(0, 0, 0))
        
        y_pos += 60
        draw.text((x_right + 15, y_pos), f"รับซื้อ", fill=(255, 255, 255), font=font_medium)
        y_pos += 55
        draw.text((x_right + 15, y_pos), f"{data['ombuy']}", fill=(255, 255, 255), font=font_medium, stroke_width=2, stroke_fill=(0, 0, 0))
        
        # เส้นแบ่ง
        y_pos = 485
        draw.line([(80, y_pos), (self.width - 80, y_pos)], fill=(255, 255, 255), width=2)
        
        # การเปลี่ยนแปลง
        y_pos = 515
        try:
            diff_value = int(data['diff'].replace(',', ''))
            if diff_value > 0:
                trend_text = f"เพิ่มขึ้น {data['diff']} บาท"
                trend_color = (0, 255, 0)
                trend_icon = "↑"
            elif diff_value < 0:
                trend_text = f"ลดลง {abs(diff_value):,} บาท"
                trend_color = (255, 50, 50)
                trend_icon = "↓"
            else:
                trend_text = f"ไม่เปลี่ยนแปลง"
                trend_color = (255, 255, 255)
                trend_icon = "→"
        except:
            trend_text = f"ไม่เปลี่ยนแปลง"
            trend_color = (255, 255, 255)
            trend_icon = "→"
        
        trend_full = f"{trend_icon} {trend_text}"
        trend_bbox = draw.textbbox((0, 0), trend_full, font=font_large)
        trend_width = trend_bbox[2] - trend_bbox[0]
        draw.text(
            ((self.width - trend_width) / 2, y_pos),
            trend_full,
            fill=trend_color,
            font=font_large,
            stroke_width=3,
            stroke_fill=(0, 0, 0)
        )
        
        return img
    
    def create_gold_price_image_simple(self):
        """สร้างรูปภาพแบบเรียบง่าย - ปรับปรุงใหม่"""
        if not self.latest_price:
            return None
        
        data = self.latest_price
        
        # สร้างพื้นหลังสีเข้ม
        img = Image.new('RGB', (self.width, self.height), (25, 25, 35))
        draw = ImageDraw.Draw(img)
        
        # Fonts - ปรับขนาดให้สมดุล
        font_title = self.get_font(72, bold=True)
        font_large = self.get_font(52, bold=True)
        font_medium = self.get_font(44, bold=False)
        font_small = self.get_font(36, bold=False)
        
        # หัวข้อ
        y_pos = 70
        title = "ราคาทองคำ"
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((self.width - title_width) / 2, y_pos),
            title,
            fill=(255, 215, 0),
            font=font_title,
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )
        
        # วันที่
        y_pos = 160
        date_text = f"อัปเดต: {data['asdate']}"
        date_bbox = draw.textbbox((0, 0), date_text, font=font_small)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(
            ((self.width - date_width) / 2, y_pos),
            date_text,
            fill=(180, 180, 180),
            font=font_small
        )
        
        # เส้นแบ่ง
        y_pos = 220
        draw.line([(100, y_pos), (self.width - 100, y_pos)], fill=(255, 215, 0), width=2)
        
        # ทองคำแท่ง
        y_pos = 255
        draw.text((100, y_pos), "ทองแท่ง 96.5%", fill=(255, 215, 0), font=font_large)
        y_pos += 60
        draw.text((120, y_pos), f"รับซื้อ: {data['blbuy']}", fill=(255, 255, 255), font=font_medium)
        y_pos += 55
        draw.text((120, y_pos), f"ขาย: {data['blsell']}", fill=(255, 255, 255), font=font_medium)
        
        # ทองรูปพรรณ
        y_pos = 255
        x_right = 650
        draw.text((x_right, y_pos), "ทองรูปพรรณ 96.5%", fill=(255, 215, 0), font=font_large)
        y_pos += 60
        draw.text((x_right + 20, y_pos), f"รับซื้อ:", fill=(255, 255, 255), font=font_medium)
        y_pos += 55
        draw.text((x_right + 20, y_pos), f"{data['ombuy']}", fill=(255, 255, 255), font=font_medium)
        
        # เส้นแบ่ง
        y_pos = 490
        draw.line([(100, y_pos), (self.width - 100, y_pos)], fill=(255, 215, 0), width=2)
        
        # การเปลี่ยนแปลง
        y_pos = 520
        try:
            diff_value = int(data['diff'].replace(',', ''))
            if diff_value > 0:
                trend_text = f"↑ เพิ่มขึ้น {data['diff']} บาท"
                trend_color = (0, 255, 100)
            elif diff_value < 0:
                trend_text = f"↓ ลดลง {abs(diff_value):,} บาท"
                trend_color = (255, 50, 50)
            else:
                trend_text = f"→ ไม่เปลี่ยนแปลง"
                trend_color = (200, 200, 200)
        except:
            trend_text = f"→ ไม่เปลี่ยนแปลง"
            trend_color = (200, 200, 200)
        
        trend_bbox = draw.textbbox((0, 0), trend_text, font=font_large)
        trend_width = trend_bbox[2] - trend_bbox[0]
        draw.text(
            ((self.width - trend_width) / 2, y_pos),
            trend_text,
            fill=trend_color,
            font=font_large,
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )
        
        return img
    
    def create_gold_price_image_premium(self):
        """สร้างรูปภาพแบบพรีเมียม - ปรับปรุงใหม่"""
        if not self.latest_price:
            return None
        
        data = self.latest_price
        
        # สร้างพื้นหลัง gradient (เข้มสวยงาม)
        img = self.create_gradient_background(
            (15, 15, 30),    # Dark blue
            (30, 15, 45)     # Purple
        )
        
        draw = ImageDraw.Draw(img)
        
        # Fonts - ปรับขนาดให้สมดุล
        font_title = self.get_font(70, bold=True)
        font_large = self.get_font(50, bold=True)
        font_medium = self.get_font(42, bold=False)
        font_small = self.get_font(34, bold=False)
        
        # วาดกรอบทองหลายชั้น
        margin = 25
        for i in range(4):
            draw.rectangle(
                [(margin + i*2, margin + i*2), (self.width - margin - i*2, self.height - margin - i*2)],
                outline=(255, 215, 0),
                width=2
            )
        
        # พื้นหลังกล่องข้อมูลโปร่งแสง
        box_margin = 50
        # สร้าง overlay สีดำโปร่งแสง
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [(box_margin, 70), (self.width - box_margin, self.height - 70)],
            fill=(0, 0, 0, 180),
            outline=(255, 215, 0),
            width=4
        )
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)  # สร้าง draw ใหม่หลัง paste overlay
        
        # หัวข้อ
        y_pos = 80
        title = "ราคาทองคำวันนี้"
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((self.width - title_width) / 2, y_pos),
            title,
            fill=(255, 215, 0),
            font=font_title,
            stroke_width=3,
            stroke_fill=(0, 0, 0)
        )
        
        # วันที่และครั้งที่
        y_pos = 165
        date_text = f"อัปเดต: {data['asdate']} (ครั้งที่ {data['nqy']})"
        date_bbox = draw.textbbox((0, 0), date_text, font=font_small)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(
            ((self.width - date_width) / 2, y_pos),
            date_text,
            fill=(200, 200, 200),
            font=font_small
        )
        
        # เส้นแบ่งทอง
        y_pos = 220
        draw.line([(90, y_pos), (self.width - 90, y_pos)], fill=(255, 215, 0), width=3)
        
        # ทองคำแท่ง (ซ้าย)
        y_pos = 255
        x_left = 90
        draw.text((x_left, y_pos), "ทองคำแท่ง 96.5%", fill=(255, 215, 0), font=font_large, stroke_width=2, stroke_fill=(0, 0, 0))
        y_pos += 60
        draw.text((x_left + 20, y_pos), f"รับซื้อ: {data['blbuy']}", fill=(255, 255, 255), font=font_medium)
        y_pos += 55
        draw.text((x_left + 20, y_pos), f"ขาย: {data['blsell']}", fill=(255, 255, 255), font=font_medium)
        
        # ทองรูปพรรณ (ขวา)
        y_pos = 255
        x_right = 640
        draw.text((x_right, y_pos), "ทองรูปพรรณ 96.5%", fill=(255, 215, 0), font=font_large, stroke_width=2, stroke_fill=(0, 0, 0))
        y_pos += 60
        draw.text((x_right + 20, y_pos), f"รับซื้อ:", fill=(255, 255, 255), font=font_medium)
        y_pos += 55
        draw.text((x_right + 20, y_pos), f"{data['ombuy']}", fill=(255, 255, 255), font=font_medium)
        
        # เส้นแบ่งทอง
        y_pos = 480
        draw.line([(90, y_pos), (self.width - 90, y_pos)], fill=(255, 215, 0), width=3)
        
        # การเปลี่ยนแปลง
        y_pos = 510
        try:
            diff_value = int(data['diff'].replace(',', ''))
            if diff_value > 0:
                trend_text = f"↑ เพิ่มขึ้น {data['diff']} บาท"
                trend_color = (0, 255, 100)
            elif diff_value < 0:
                trend_text = f"↓ ลดลง {abs(diff_value):,} บาท"
                trend_color = (255, 50, 50)
            else:
                trend_text = f"→ ไม่เปลี่ยนแปลง"
                trend_color = (200, 200, 200)
        except:
            trend_text = f"→ ไม่เปลี่ยนแปลง"
            trend_color = (200, 200, 200)
        
        trend_bbox = draw.textbbox((0, 0), trend_text, font=font_large)
        trend_width = trend_bbox[2] - trend_bbox[0]
        draw.text(
            ((self.width - trend_width) / 2, y_pos),
            trend_text,
            fill=trend_color,
            font=font_large,
            stroke_width=3,
            stroke_fill=(0, 0, 0)
        )
        
        return img
    
    def save_image(self, img, filename="facebook_gold_post.jpg"):
        """บันทึกรูปภาพ"""
        try:
            filepath = self.output_dir / filename
            img.save(filepath, quality=95)
            print(f"✅ บันทึกรูปภาพไปที่: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ ไม่สามารถบันทึกรูปภาพ: {e}")
            return None


def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("🎨 Facebook Image Generator - Gold Price")
    print("=" * 60)
    
    # สร้าง instance
    img_gen = FacebookImageGenerator()
    
    # โหลดข้อมูล
    if not img_gen.load_latest_price():
        return
    
    print("\n🎨 เลือกสไตล์รูปภาพ:")
    print("1. Modern (โมเดิร์น - พื้นหลังทอง)")
    print("2. Simple (เรียบง่าย - พื้นหลังดำ)")
    print("3. Premium (พรีเมียม - มีกรอบและเอฟเฟกต์)")
    print("4. สร้างทุกสไตล์")
    
    choice = input("\n👉 เลือก (1-4): ").strip()
    
    images = {}
    
    if choice == "1":
        images["modern"] = img_gen.create_gold_price_image_modern()
    elif choice == "2":
        images["simple"] = img_gen.create_gold_price_image_simple()
    elif choice == "3":
        images["premium"] = img_gen.create_gold_price_image_premium()
    elif choice == "4":
        images["modern"] = img_gen.create_gold_price_image_modern()
        images["simple"] = img_gen.create_gold_price_image_simple()
        images["premium"] = img_gen.create_gold_price_image_premium()
    else:
        print("❌ ตัวเลือกไม่ถูกต้อง")
        return
    
    # บันทึกรูปภาพ
    for style, img in images.items():
        if img:
            filename = f"facebook_gold_{style}.jpg"
            img_gen.save_image(img, filename)
    
    print("\n✅ เสร็จสิ้น!")


if __name__ == "__main__":
    main()
