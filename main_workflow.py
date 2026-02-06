import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime

# ========== Configuration ==========
DB_FILE = "gold_tracker.db"
GOLD_DATA_FILE = "data/gold_prices.json"

# ========== Database Functions ==========
def init_database():
    """Initialize SQLite database to track processed gold updates."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nqy TEXT NOT NULL,
            asdate TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(nqy, asdate)
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def is_already_processed(nqy, asdate):
    """Check if this update has already been processed."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM processed_updates 
        WHERE nqy = ? AND asdate = ?
    """, (nqy, asdate))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def mark_as_processed(nqy, asdate):
    """Mark this update as processed in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO processed_updates (nqy, asdate)
            VALUES (?, ?)
        """, (nqy, asdate))
        conn.commit()
        print(f"✅ Marked as processed: nqy={nqy}, asdate={asdate}")
    except sqlite3.IntegrityError:
        print(f"⚠️  Already exists in database: nqy={nqy}, asdate={asdate}")
    finally:
        conn.close()

# ========== Workflow Functions ==========
def run_script(script_name, description):
    """Run a Python script and return success status."""
    print(f"\n{'='*60}")
    print(f"🔄 Running: {description}")
    print(f"   Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
            return True
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} timed out (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def get_latest_gold_data():
    """Read the latest gold price from JSON file."""
    if not os.path.exists(GOLD_DATA_FILE):
        print(f"❌ File not found: {GOLD_DATA_FILE}")
        return None
    
    try:
        with open(GOLD_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data[-1]  # Return last entry
            else:
                print("❌ No data in gold_prices.json")
                return None
    except Exception as e:
        print(f"❌ Error reading {GOLD_DATA_FILE}: {e}")
        return None

# ========== Main Workflow ==========
def main():
    print("\n" + "="*60)
    print("  🏆 GOLD PRICE AUTOMATION WORKFLOW")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 0: Initialize database
    init_database()
    
    # Step 1: Fetch latest gold prices
    print("\n📡 STEP 1: Fetching latest gold prices...")
    if not run_script("getgold_old.py", "Gold Price Scraper"):
        print("❌ Failed to fetch gold prices. Aborting workflow.")
        sys.exit(1)
    
    # Step 2: Check if data is new
    print("\n🔍 STEP 2: Checking for new data...")
    latest_data = get_latest_gold_data()
    
    if not latest_data:
        print("❌ No data available. Aborting workflow.")
        sys.exit(1)
    
    nqy = latest_data.get("nqy", "")
    asdate = latest_data.get("asdate", "")
    
    print(f"📊 Latest data: nqy={nqy}, asdate={asdate}")
    
    if is_already_processed(nqy, asdate):
        print(f"⏭️  This update has already been processed. Skipping.")
        print(f"   (nqy={nqy}, asdate={asdate})")
        sys.exit(0)
    
    print(f"🆕 New data detected! Proceeding with workflow...")
    
    # Step 3: Generate video
    print("\n🎬 STEP 3: Generating video...")
    if not run_script("app.py", "Video Generator"):
        print("⚠️  Video generation failed, but continuing...")
    
    # Step 4: Post to Blogger
    print("\n📝 STEP 4: Posting to Blogger...")
    if not run_script("pypost_gold.py", "Blogger Publisher"):
        print("⚠️  Blogger posting failed, but continuing...")
    
    # Step 5: Send Telegram notification
    print("\n📱 STEP 5: Sending Telegram notification...")
    if not run_script("telegram_notify.py", "Telegram Notifier"):
        print("⚠️  Telegram notification failed, but continuing...")
    
    # Step 6: Mark as processed
    print("\n💾 STEP 6: Marking as processed...")
    mark_as_processed(nqy, asdate)
    
    # Summary
    print("\n" + "="*60)
    print("  ✅ WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*60)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Processed: nqy={nqy}, asdate={asdate}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
