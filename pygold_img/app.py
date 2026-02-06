from flask import Flask, render_template
import json
import os

app = Flask(__name__)

def load_data():
    filename = 'gold_prices.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # ไม่ต้อง reverse ตรงนี้ทันที เพื่อให้คำนวณง่าย
            return data
    return []

def format_thai_date(date_str):
    thai_months = [
        "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    try:
        day, month, year = date_str.split('/')
        return f"{int(day)} {thai_months[int(month)]} {year}"
    except:
        return date_str

@app.route('/')
def index():
    raw_data = load_data()
    
    # 1. คำนวณผลรวม diff ทั้งหมด (Total Change)
    total_diff_val = 0
    for item in raw_data:
        # ลบลูกน้ำออกแล้วแปลงเป็นตัวเลขเพื่อคำนวณ
        val = int(item['diff'].replace(',', ''))
        total_diff_val += val
    
    # จัดรูปแบบกลับเป็น string ที่มีลูกน้ำ (เช่น "4,000")
    total_diff_str = "{:,}".format(total_diff_val)

    # 2. เตรียมข้อมูลสำหรับแสดงผล (Reverse เพื่อให้ล่าสุดอยู่บนสุด)
    display_data = raw_data.copy()
    display_data.reverse()

    for item in display_data:
        dt_parts = item['asdate'].split(' ')
        item['display_date'] = format_thai_date(dt_parts[0])
        item['display_time'] = dt_parts[1]

    # ส่ง total_diff_str ไปที่ Template ด้วย
    return render_template('index.html', prices=display_data, total_diff=total_diff_str, total_val=total_diff_val)

if __name__ == '__main__':
    app.run(debug=True, port=5000)