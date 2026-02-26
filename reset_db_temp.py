import sqlite3
import os

db_path = r'E:\openclaw\gold_vertical_panel_openclaw\gold_tracker.db'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # ลบข้อมูลรอบล่าสุด
    cursor.execute("DELETE FROM processed_updates WHERE nqy='7' AND asdate='24/02/2569 11:32'")
    conn.commit()
    print(f"[OK] Deleted {cursor.rowcount} rows from gold_tracker.db")
    conn.close()
except Exception as e:
    print(f"[ERROR] {e}")
