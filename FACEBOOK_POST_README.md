# 📱 Facebook Post Generator สำหรับราคาทองคำ

## 🎯 ภาพรวม

ระบบสร้างโพสต์ Facebook สำหรับราคาทองคำอัตโนมัติ รองรับหลายรูปแบบและสามารถโพสต์ไปยัง Facebook Page ได้โดยตรง

## 📦 ไฟล์ที่เกี่ยวข้อง

- **`facebook_post.py`** - สร้างโพสต์ราคาทองคำ (4 รูปแบบ)
- **`facebook_auto_post.py`** - โพสต์ไปยัง Facebook อัตโนมัติผ่าน API
- **`facebook_config.json`** - ไฟล์ config สำหรับ Facebook API

## 🚀 วิธีใช้งาน

### 1️⃣ สร้างโพสต์ (ไม่โพสต์ไปยัง Facebook)

```bash
python facebook_post.py
```

**ตัวเลือก:**
- `1` - โพสต์แบบพื้นฐาน (Basic)
- `2` - โพสต์แบบสั้น (Short) - เหมาะสำหรับ Story
- `3` - โพสต์แบบละเอียด (Detailed) - แนะนำ!
- `4` - โพสต์พร้อมเปรียบเทียบ (Comparison)
- `5` - สร้างทุกรูปแบบพร้อมกัน

**ผลลัพธ์:**
- โพสต์จะถูกบันทึกในโฟลเดอร์ `out/`
- ไฟล์: `facebook_post_basic.txt`, `facebook_post_short.txt`, etc.

---

### 2️⃣ โพสต์ไปยัง Facebook อัตโนมัติ

#### ขั้นตอนที่ 1: ตั้งค่า Facebook API

1. **สร้าง Facebook App**
   - ไปที่: https://developers.facebook.com/
   - คลิก "My Apps" > "Create App"
   - เลือก "Business" type
   - ตั้งชื่อ App (เช่น "Gold Price Bot")

2. **เพิ่ม Product: Facebook Login**
   - ในหน้า Dashboard ของ App
   - คลิก "Add Product"
   - เลือก "Facebook Login"

3. **ดึง Page Access Token**
   - ไปที่: https://developers.facebook.com/tools/explorer/
   - เลือก App ที่สร้างไว้
   - เลือก "Get User Access Token"
   - เลือก permissions:
     - `pages_manage_posts`
     - `pages_read_engagement`
   - คลิก "Generate Access Token"
   - **คัดลอก Token** (จะใช้ในขั้นตอนถัดไป)

4. **หา Page ID**
   - ไปที่ Facebook Page ของคุณ
   - คลิก "About"
   - เลื่อนลงไปหา "Page ID"
   - **คัดลอก Page ID**

#### ขั้นตอนที่ 2: แก้ไขไฟล์ Config

รันสคริปต์ครั้งแรกเพื่อสร้างไฟล์ config:

```bash
python facebook_auto_post.py
```

จะได้ไฟล์ `facebook_config.json` แก้ไขดังนี้:

```json
{
  "access_token": "YOUR_PAGE_ACCESS_TOKEN_HERE",
  "page_id": "YOUR_PAGE_ID_HERE"
}
```

ใส่ค่าที่ได้จากขั้นตอนที่ 1:

```json
{
  "access_token": "EAABsbCS1iHgBO...",
  "page_id": "123456789012345"
}
```

#### ขั้นตอนที่ 3: รันสคริปต์

```bash
python facebook_auto_post.py
```

**ตัวเลือก:**
1. เลือกรูปแบบโพสต์ (1-4)
2. เลือกประเภทการโพสต์:
   - โพสต์ข้อความอย่างเดียว
   - โพสต์พร้อมวิดีโอ (จาก `out/output.mp4`)

---

## 📝 ตัวอย่างโพสต์

### โพสต์แบบพื้นฐาน (Basic)
```
💰 ราคาทองคำวันนี้ 💰
━━━━━━━━━━━━━━━━━━━━

📅 อัพเดท: 06/02/2569 10:33
🔄 ครั้งที่: 11

🏆 ทองคำแท่ง 96.5%
├─ 💵 รับซื้อ: 72,300.00 บาท
└─ 💰 ขาย: 72,500.00 บาท

💍 ทองรูปพรรณ 96.5%
├─ 💵 รับซื้อ: 70,857.84 บาท
└─ 💰 ขาย: 73,300.00 บาท

📈 ขึ้น 100 บาท
```

### โพสต์แบบสั้น (Short)
```
💰 ราคาทองคำ 06/02/2569 10:33

🏆 ทองแท่ง: 72,300.00 / 72,500.00
💍 ทองรูปพรรณ: 70,857.84 / 73,300.00

📈 ขึ้น 100 บาท
```

### โพสต์แบบละเอียด (Detailed)
```
💰✨ อัพเดทราคาทองคำ ✨💰
━━━━━━━━━━━━━━━━━━━━━━━━

📅 วันที่: 06/02/2569 10:33
🔄 อัพเดทครั้งที่: 11 (วันนี้)

🏆 ทองคำแท่ง 96.5%
┏━━━━━━━━━━━━━━━━━━━
┃ 💵 รับซื้อ: 72,300.00 บาท
┃ 💰 ขายออก: 72,500.00 บาท
┗━━━━━━━━━━━━━━━━━━━

💡 ราคาค่อนข้างคงที่ รอจังหวะที่เหมาะสม

📌 ข้อมูลจาก: สมาคมค้าทองคำ
⏰ อัพเดทอัตโนมัติทุก 30 นาที

#ราคาทอง #ทองคำ #GoldPrice
```

---

## 🔄 การใช้งานอัตโนมัติ

### ตัวเลือก 1: ใช้ Task Scheduler (Windows)

สร้างไฟล์ `auto_facebook_post.bat`:

```batch
@echo off
cd /d E:\gold_vertical_panel
python facebook_auto_post.py
pause
```

ตั้งค่า Task Scheduler:
1. เปิด Task Scheduler
2. Create Basic Task
3. ตั้งเวลา (เช่น ทุก 1 ชั่วโมง)
4. Action: Start a program
5. Program: `E:\gold_vertical_panel\auto_facebook_post.bat`

### ตัวเลือก 2: เพิ่มใน Workflow ที่มีอยู่

แก้ไข `main_workflow.py` เพื่อเพิ่มการโพสต์ Facebook:

```python
# เพิ่มในส่วนท้ายของ workflow
from facebook_auto_post import FacebookAutoPost
from facebook_post import FacebookGoldPost

# สร้างโพสต์และโพสต์ไปยัง Facebook
fb_post_gen = FacebookGoldPost()
fb_post_gen.load_latest_price()
post_text = fb_post_gen.create_post_detailed()

fb_auto = FacebookAutoPost()
fb_auto.post_to_facebook(post_text)
```

---

## 🛠️ การติดตั้ง Dependencies

```bash
pip install requests
```

(ไลบรารีอื่นๆ ติดตั้งไว้แล้วจากโปรเจกต์เดิม)

---

## ⚠️ ข้อควรระวัง

1. **Access Token มีอายุจำกัด**
   - User Access Token: 1-2 ชั่วโมง
   - Page Access Token: ไม่หมดอายุ (แนะนำ)
   - ควรใช้ Page Access Token ที่ไม่หมดอายุ

2. **Rate Limiting**
   - Facebook จำกัดจำนวนโพสต์ต่อชั่วโมง
   - ไม่ควรโพสต์บ่อยเกินไป (แนะนำ 1-2 ชั่วโมงต่อครั้ง)

3. **Permissions**
   - ต้องมี `pages_manage_posts` permission
   - ต้องเป็น Admin ของ Page

---

## 🎨 การปรับแต่ง

### เปลี่ยนรูปแบบโพสต์

แก้ไขฟังก์ชันใน `facebook_post.py`:
- `create_post_basic()` - โพสต์พื้นฐาน
- `create_post_short()` - โพสต์สั้น
- `create_post_detailed()` - โพสต์ละเอียด
- `create_post_with_comparison()` - โพสต์เปรียบเทียบ

### เพิ่ม Hashtags

แก้ไขในส่วนท้ายของแต่ละฟังก์ชัน:

```python
#ราคาทอง #ทองคำ #YourCustomHashtag
```

---

## 📊 สถิติการใช้งาน

| ฟีเจอร์ | สถานะ |
|---------|-------|
| ✅ สร้างโพสต์ข้อความ | พร้อมใช้งาน |
| ✅ โพสต์ไปยัง Facebook | พร้อมใช้งาน |
| ✅ โพสต์พร้อมวิดีโอ | พร้อมใช้งาน |
| ⏳ โพสต์พร้อมรูปภาพ | รองรับแล้ว (ยังไม่ทดสอบ) |
| ⏳ Schedule Posts | อยู่ระหว่างพัฒนา |

---

## 🆘 การแก้ปัญหา

### ปัญหา: "Invalid OAuth access token"
**วิธีแก้:** 
- ตรวจสอบว่า Access Token ยังไม่หมดอายุ
- สร้าง Access Token ใหม่

### ปัญหา: "Permissions error"
**วิธีแก้:**
- ตรวจสอบว่ามี `pages_manage_posts` permission
- ตรวจสอบว่าเป็น Admin ของ Page

### ปัญหา: "Video upload failed"
**วิธีแก้:**
- ตรวจสอบว่าไฟล์วิดีโออยู่ที่ `out/output.mp4`
- ตรวจสอบขนาดไฟล์ (ไม่ควรเกิน 1GB)
- ตรวจสอบ internet connection

---

## 📞 ติดต่อ & สนับสนุน

หากมีปัญหาหรือข้อสงสัย:
1. ตรวจสอบ Error Message
2. อ่าน Facebook API Documentation: https://developers.facebook.com/docs/graph-api
3. ตรวจสอบ Access Token: https://developers.facebook.com/tools/debug/accesstoken/

---

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ

---

**สร้างโดย:** Gold Price Automation System  
**อัพเดทล่าสุด:** 6 กุมภาพันธ์ 2569
