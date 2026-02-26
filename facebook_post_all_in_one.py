"""
Facebook Post All-in-One
สร้างโพสต์ Facebook ครบวงจร (ข้อความ + รูปภาพ + โพสต์อัตโนมัติ)
"""

import json
import sys
from pathlib import Path
from facebook_post import FacebookGoldPost
from facebook_image_post import FacebookImageGenerator
from facebook_auto_post import FacebookAutoPost

class FacebookPostAllInOne:
    def __init__(self):
        self.post_generator = FacebookGoldPost()
        self.image_generator = FacebookImageGenerator()
        self.auto_poster = FacebookAutoPost()
        
    def create_complete_post(self, post_style="detailed", image_style="premium"):
        """สร้างโพสต์ครบวงจร"""
        print("=" * 70)
        print("🚀 Facebook Post All-in-One - Gold Price")
        print("=" * 70)
        
        # โหลดข้อมูล
        print("\n📊 กำลังโหลดข้อมูลราคาทองคำ...")
        if not self.post_generator.load_latest_price():
            print("❌ ไม่สามารถโหลดข้อมูลได้")
            return False
        
        if not self.image_generator.load_latest_price():
            print("❌ ไม่สามารถโหลดข้อมูลได้")
            return False
        
        print("✅ โหลดข้อมูลสำเร็จ")
        
        # สร้างโพสต์ข้อความ
        print("\n📝 กำลังสร้างโพสต์ข้อความ...")
        post_text = None
        
        if post_style == "basic":
            post_text = self.post_generator.create_post_basic()
        elif post_style == "short":
            post_text = self.post_generator.create_post_short()
        elif post_style == "detailed":
            post_text = self.post_generator.create_post_detailed()
        elif post_style == "comparison":
            post_text = self.post_generator.create_post_with_comparison()
        
        if not post_text:
            print("❌ ไม่สามารถสร้างโพสต์ได้")
            return False
        
        # บันทึกโพสต์
        filename = f"facebook_post_{post_style}.txt"
        self.post_generator.save_post_to_file(post_text, filename)
        print(f"✅ สร้างโพสต์ข้อความสำเร็จ: out/{filename}")
        
        # สร้างรูปภาพ
        print("\n🎨 กำลังสร้างรูปภาพโพสต์...")
        image = None
        
        if image_style == "modern":
            image = self.image_generator.create_gold_price_image_modern()
        elif image_style == "simple":
            image = self.image_generator.create_gold_price_image_simple()
        elif image_style == "premium":
            image = self.image_generator.create_gold_price_image_premium()
        
        if not image:
            print("❌ ไม่สามารถสร้างรูปภาพได้")
            return False
        
        # บันทึกรูปภาพ
        image_filename = f"facebook_gold_{image_style}.jpg"
        image_path = self.image_generator.save_image(image, image_filename)
        print(f"✅ สร้างรูปภาพสำเร็จ: {image_path}")
        
        # แสดงตัวอย่าง
        print("\n" + "=" * 70)
        print("📄 ตัวอย่างโพสต์:")
        print("=" * 70)
        print(post_text)
        print("=" * 70)
        
        return {
            "text": post_text,
            "image_path": image_path,
            "text_file": f"out/{filename}"
        }
    
    def interactive_mode(self):
        """โหมดแบบโต้ตอบ"""
        print("=" * 70)
        print("🎯 Facebook Post All-in-One - Interactive Mode")
        print("=" * 70)
        
        # เลือกสไตล์โพสต์
        print("\n📝 เลือกสไตล์โพสต์ข้อความ:")
        print("1. Basic (พื้นฐาน)")
        print("2. Short (สั้น)")
        print("3. Detailed (ละเอียด) - แนะนำ")
        print("4. Comparison (เปรียบเทียบ)")
        
        post_choice = input("\n👉 เลือก (1-4): ").strip()
        post_styles = {
            "1": "basic",
            "2": "short",
            "3": "detailed",
            "4": "comparison"
        }
        post_style = post_styles.get(post_choice, "detailed")
        
        # เลือกสไตล์รูปภาพ
        print("\n🎨 เลือกสไตล์รูปภาพ:")
        print("1. Modern (โมเดิร์น)")
        print("2. Simple (เรียบง่าย)")
        print("3. Premium (พรีเมียม) - แนะนำ")
        
        image_choice = input("\n👉 เลือก (1-3): ").strip()
        image_styles = {
            "1": "modern",
            "2": "simple",
            "3": "premium"
        }
        image_style = image_styles.get(image_choice, "premium")
        
        # สร้างโพสต์
        result = self.create_complete_post(post_style, image_style)
        
        if not result:
            print("\n❌ ไม่สามารถสร้างโพสต์ได้")
            return
        
        # ถามว่าต้องการโพสต์หรือไม่
        print("\n📤 ต้องการโพสต์ไปยัง Facebook หรือไม่?")
        print("1. โพสต์ข้อความอย่างเดียว")
        print("2. โพสต์พร้อมรูปภาพ")
        print("3. โพสต์พร้อมวิดีโอ (out/output.mp4)")
        print("4. ไม่โพสต์ (บันทึกไว้ใช้ภายหลัง)")
        
        post_to_fb = input("\n👉 เลือก (1-4): ").strip()
        
        if post_to_fb == "1":
            self.auto_poster.post_to_facebook(result["text"])
        elif post_to_fb == "2":
            self.auto_poster.post_with_image(result["text"], result["image_path"])
        elif post_to_fb == "3":
            video_path = "out/output.mp4"
            if Path(video_path).exists():
                self.auto_poster.post_with_video(result["text"], video_path)
            else:
                print(f"❌ ไม่พบไฟล์วิดีโอ: {video_path}")
        elif post_to_fb == "4":
            print("✅ บันทึกโพสต์ไว้ใช้ภายหลัง")
        else:
            print("❌ ตัวเลือกไม่ถูกต้อง")
        
        print("\n✅ เสร็จสิ้น!")
    
    def auto_mode(self, post_style="detailed", image_style="premium", auto_post=False):
        """โหมดอัตโนมัติ (สำหรับใช้ใน workflow)"""
        print("🤖 Auto Mode - Creating Facebook Post...")
        
        result = self.create_complete_post(post_style, image_style)
        
        if not result:
            return False
        
        if auto_post:
            print("\n📤 กำลังโพสต์ไปยัง Facebook อัตโนมัติ...")
            success = self.auto_poster.post_with_image(result["text"], result["image_path"])
            
            if success:
                print("✅ โพสต์ไปยัง Facebook สำเร็จ!")
                return True
            else:
                print("❌ โพสต์ไปยัง Facebook ไม่สำเร็จ")
                return False
        else:
            print("\n✅ สร้างโพสต์สำเร็จ (ยังไม่ได้โพสต์ไปยัง Facebook)")
            return True


def main():
    """ฟังก์ชันหลัก"""
    all_in_one = FacebookPostAllInOne()
    
    # ตรวจสอบ command line arguments
    if len(sys.argv) > 1:
        # Auto mode
        post_style = sys.argv[1] if len(sys.argv) > 1 else "detailed"
        image_style = sys.argv[2] if len(sys.argv) > 2 else "premium"
        auto_post = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else False
        
        all_in_one.auto_mode(post_style, image_style, auto_post)
    else:
        # Interactive mode
        all_in_one.interactive_mode()


if __name__ == "__main__":
    main()
