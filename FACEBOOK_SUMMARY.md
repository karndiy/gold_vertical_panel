# 📱 สรุปไฟล์ Facebook Post System

## 📦 ไฟล์ที่สร้างขึ้น

### 1. **facebook_post.py** - สร้างโพสต์ข้อความ
- สร้างโพสต์ 4 รูปแบบ: Basic, Short, Detailed, Comparison
- บันทึกเป็นไฟล์ .txt
- รองรับการคัดลอกไปยัง clipboard

**วิธีใช้:**
```bash
python facebook_post.py
```

---

### 2. **facebook_image_post.py** - สร้างรูปภาพโพสต์
- สร้างรูปภาพ 3 สไตล์: Modern, Simple, Premium
- ขนาด 1200x630 (เหมาะสำหรับ Facebook)
- บันทึกเป็นไฟล์ .jpg

**วิธีใช้:**
```bash
python facebook_image_post.py
```

---

### 3. **facebook_auto_post.py** - โพสต์อัตโนมัติ
- โพสต์ไปยัง Facebook Page ผ่าน API
- รองรับโพสต์ข้อความ, รูปภาพ, วิดีโอ
- ต้องตั้งค่า facebook_config.json ก่อน

**วิธีใช้:**
```bash
python facebook_auto_post.py
```

**ตั้งค่า:**
1. รันครั้งแรกเพื่อสร้างไฟล์ config
2. แก้ไข `facebook_config.json` ใส่ access_token และ page_id
3. รันอีกครั้งเพื่อโพสต์

---

### 4. **facebook_post_all_in_one.py** - ครบวงจร ⭐ แนะนำ
- รวมทุกฟีเจอร์เข้าด้วยกัน
- สร้างโพสต์ข้อความ + รูปภาพ + โพสต์อัตโนมัติ
- รองรับทั้งโหมดแบบโต้ตอบและอัตโนมัติ

**วิธีใช้:**

**โหมดแบบโต้ตอบ:**
```bash
python facebook_post_all_in_one.py
```

**โหมดอัตโนมัติ:**
```bash
python facebook_post_all_in_one.py detailed premium false
# รูปแบบ: python facebook_post_all_in_one.py [post_style] [image_style] [auto_post]
# post_style: basic, short, detailed, comparison
# image_style: modern, simple, premium
# auto_post: true, false
```

---

### 5. **run_facebook_post.bat** - Batch file สำหรับ Windows
- รันสคริปต์สร้างโพสต์อย่างรวดเร็ว
- ดับเบิลคลิกเพื่อรัน

---

### 6. **FACEBOOK_POST_README.md** - คู่มือการใช้งาน
- คู่มือละเอียดสำหรับการตั้งค่า Facebook API
- วิธีแก้ปัญหา
- ตัวอย่างการใช้งาน

---

## 🚀 Quick Start

### สร้างโพสต์แบบง่าย (ไม่โพสต์ไปยัง Facebook)

```bash
# สร้างโพสต์ข้อความ
python facebook_post.py

# สร้างรูปภาพ
python facebook_image_post.py
```

### สร้างโพสต์และโพสต์ไปยัง Facebook

```bash
# ใช้ All-in-One (แนะนำ)
python facebook_post_all_in_one.py
```

---

## 📊 ตัวอย่างผลลัพธ์

### ไฟล์ที่สร้างขึ้น (ใน folder `out/`)

**โพสต์ข้อความ:**
- `facebook_post_basic.txt`
- `facebook_post_short.txt`
- `facebook_post_detailed.txt`
- `facebook_post_comparison.txt`

**รูปภาพ:**
- `facebook_gold_modern.jpg` - พื้นหลังสีทอง
- `facebook_gold_simple.jpg` - พื้นหลังสีดำ
- `facebook_gold_premium.jpg` - มีกรอบและเอฟเฟกต์

---

## 🔧 การตั้งค่า Facebook API

### ขั้นตอนย่อ:

1. **สร้าง Facebook App** ที่ https://developers.facebook.com/
2. **ดึง Page Access Token** จาก Graph API Explorer
3. **แก้ไข facebook_config.json:**
   ```json
   {
     "access_token": "YOUR_PAGE_ACCESS_TOKEN",
     "page_id": "YOUR_PAGE_ID"
   }
   ```

**ดูรายละเอียดเพิ่มเติมใน:** `FACEBOOK_POST_README.md`

---

## 🔄 การใช้งานอัตโนมัติ

### เพิ่มใน Workflow ที่มีอยู่

แก้ไข `main_workflow.py`:

```python
# เพิ่มในส่วนท้าย
from facebook_post_all_in_one import FacebookPostAllInOne

# สร้างและโพสต์อัตโนมัติ
fb_all = FacebookPostAllInOne()
fb_all.auto_mode(
    post_style="detailed",
    image_style="premium",
    auto_post=True  # ตั้งเป็น True เพื่อโพสต์อัตโนมัติ
)
```

### ใช้ Task Scheduler (Windows)

สร้างไฟล์ `auto_facebook_workflow.bat`:

```batch
@echo off
cd /d E:\gold_vertical_panel
python facebook_post_all_in_one.py detailed premium true
```

ตั้งเวลาใน Task Scheduler ให้รันทุก 1-2 ชั่วโมง

---

## 📝 ตัวอย่างโพสต์

### Detailed Style (แนะนำ)
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

💍 ทองรูปพรรณ 96.5%
┏━━━━━━━━━━━━━━━━━━━
┃ 💵 รับซื้อ: 70,857.84 บาท
┃ 💰 ขายออก: 73,300.00 บาท
┗━━━━━━━━━━━━━━━━━━━

📊 ข้อมูลตลาดโลก
┏━━━━━━━━━━━━━━━━━━━
┃ 🌍 Gold Spot: $4,822.00/ออนซ์
┃ 💱 USD/THB: 31.72 บาท
┗━━━━━━━━━━━━━━━━━━━

📈 ขึ้น การเปลี่ยนแปลง: 100 บาท
🟢 เพิ่มขึ้น

💡 ราคาค่อนข้างคงที่ รอจังหวะที่เหมาะสม

━━━━━━━━━━━━━━━━━━━━━━━━
📌 ข้อมูลจาก: สมาคมค้าทองคำ
⏰ อัพเดทอัตโนมัติทุก 30 นาที

#ราคาทอง #ราคาทองวันนี้ #ทองคำ #GoldPrice
#ทองคำแท่ง #ทองรูปพรรณ #อัพเดทราคาทอง
#ลงทุนทอง #ซื้อทอง #ขายทอง #ตลาดทอง
```

---

## 🎨 รูปภาพที่สร้างขึ้น

ดูตัวอย่างรูปภาพใน folder `out/`:
- **Modern** - พื้นหลัง gradient สีทอง
- **Simple** - พื้นหลังสีดำ เรียบง่าย
- **Premium** - มีกรอบทอง เอฟเฟกต์พิเศษ

---

## ⚠️ ข้อควรระวัง

1. **Access Token หมดอายุ** - ต้องสร้างใหม่เป็นระยะ
2. **Rate Limiting** - ไม่ควรโพสต์บ่อยเกินไป (แนะนำ 1-2 ชั่วโมงต่อครั้ง)
3. **Permissions** - ต้องมี `pages_manage_posts` permission

---

## 📞 การแก้ปัญหา

### ปัญหา: "Invalid OAuth access token"
- สร้าง Access Token ใหม่

### ปัญหา: "Permissions error"
- ตรวจสอบว่ามี `pages_manage_posts` permission
- ตรวจสอบว่าเป็น Admin ของ Page

### ปัญหา: "ไม่สามารถโหลดข้อมูลได้"
- ตรวจสอบว่ามีไฟล์ `data/gold_prices.json`
- รัน `python getgold.py` เพื่ออัพเดทข้อมูล

---

## 🎯 สรุป

| ฟีเจอร์ | ไฟล์ | สถานะ |
|---------|------|-------|
| สร้างโพสต์ข้อความ | facebook_post.py | ✅ พร้อมใช้งาน |
| สร้างรูปภาพ | facebook_image_post.py | ✅ พร้อมใช้งาน |
| โพสต์อัตโนมัติ | facebook_auto_post.py | ✅ พร้อมใช้งาน |
| All-in-One | facebook_post_all_in_one.py | ✅ พร้อมใช้งาน |

---

**สร้างโดย:** Gold Price Automation System  
**วันที่:** 6 กุมภาพันธ์ 2569  
**เวอร์ชัน:** 1.0
