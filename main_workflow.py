import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
import requests # Moved import to top

# Get the directory of the current script (main_workflow.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add script directory to Python path for importing local modules
sys.path.append(SCRIPT_DIR)
from facebook_post import FacebookGoldPost
from facebook_auto_post import FacebookAutoPost

# ========== Configuration ==========
DB_FILE = os.path.join(SCRIPT_DIR, "gold_tracker.db") # Use absolute path
GOLD_DATA_FILE = os.path.join(SCRIPT_DIR, "data", "gold_prices.json") # Use absolute path

# Define output paths for app.py
APP_OUTPUT_VIDEO_PATH = os.path.join(SCRIPT_DIR, "out", "output.mp4")
APP_OUTPUT_IMAGE_PATH = os.path.join(SCRIPT_DIR, "out", "output_panel.jpg")

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
    print("[OK] Database initialized")

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
        print(f"[OK] Marked as processed: nqy={nqy}, asdate={asdate}")
    except sqlite3.IntegrityError:
        print(f"[WARN] Already exists in database: nqy={nqy}, asdate={asdate}")
    finally:
        conn.close()

# ========== Workflow Functions ==========
def run_script(script_name, description, *args):
    """Run a Python script with optional arguments and return success status."""
    print(f"\n{'='*60}")
    print(f"[RUN] Running: {description}")
    print(f"   Script: {script_name}")
    print(f"   Args: {args}") # Log arguments
    print(f"{'='*60}")
    
    command = [sys.executable, script_name] + list(args)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,  # Ensure subprocess runs from the main script's directory
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
            return True
        else:
            print(f"[ERROR] {description} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
            if result.stdout:
                print(f"Output (if any):\n{result.stdout}") # Also print stdout on error
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {description} timed out (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"[ERROR] Error running {script_name}: {e}")
        return False

def get_latest_gold_data():
    """Read the latest gold price from JSON file."""
    if not os.path.exists(GOLD_DATA_FILE):
        print(f"[ERROR] File not found: {GOLD_DATA_FILE}")
        return None
    
    try:
        with open(GOLD_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data[-1]  # Return last entry
            else:
                print("[ERROR] No data in gold_prices.json")
                return None
    except Exception as e:
        print(f"[ERROR] Error reading {GOLD_DATA_FILE}: {e}")
        return None

# ========== Online Verification Functions ==========
ONLINE_GOLD_API_URL = 'https://karndiy.pythonanywhere.com/goldjsonv2'

def verify_gold_data_online(local_data):
    """Fetches gold data from an online API and compares it with local data."""
    print(f"[INFO] Verifying data with online API: {ONLINE_GOLD_API_URL}")
    try:
        response = requests.get(ONLINE_GOLD_API_URL, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        online_data = response.json()

        if not online_data or not isinstance(online_data, list) or len(online_data) == 0:
            print("[WARN] Online API returned no data or invalid format. Cannot verify.")
            return True # Cannot verify, so proceed assuming local is fine

        latest_online_entry = online_data[-1] # Assuming latest is last entry
        
        # Compare key fields for accuracy
        local_nqy = local_data.get("nqy")
        local_asdate = local_data.get("asdate")
        online_nqy = latest_online_entry.get("nqy")
        online_asdate = latest_online_entry.get("asdate")

        if local_nqy == online_nqy and local_asdate == online_asdate:
            print("[OK] Local data matches latest online data (nqy & asdate).")
            return True
        else:
            print("[WARN] Local data DOES NOT match latest online data (nqy or asdate differs).")
            print(f"   Local: nqy={local_nqy}, asdate={local_asdate}")
            print(f"   Online: nqy={online_nqy}, asdate={online_asdate}")
            return False # Verification failed
            
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] Online API verification timed out after 10 seconds.")
        return True # Treat as "cannot verify" rather than "failed" to avoid blocking workflow
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error fetching online data for verification: {e}")
        return True # Treat as "cannot verify"
    except json.JSONDecodeError:
        print("[ERROR] Online API returned invalid JSON. Cannot verify.")
        return True # Treat as "cannot verify"
    except Exception as e:
        print(f"[ERROR] Unexpected error during online data verification: {e}")
        return True # Treat as "cannot verify"

# ========== Main Workflow ==========
def main():
    print("\n" + "='*60}")
    print("  [INFO] GOLD PRICE AUTOMATION WORKFLOW")
    print("='*60}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 0: Initialize database
    init_database()
    
    # Step 1: Fetch latest gold prices
    print("\n[INFO] STEP 1: Fetching latest gold prices...")
    if not run_script("getgold_old.py", "Gold Price Scraper"):
        print("[ERROR] Failed to fetch gold prices. Aborting workflow.")
        sys.exit(1)
    
    # Step 2: Check if data is new
    print("\n[INFO] STEP 2: Checking for new data...")
    latest_data = get_latest_gold_data()

    if not latest_data:
        print("[ERROR] No local data available after scraping. Aborting workflow.")
        sys.exit(1)

    # NEW STEP: Verify local data against online API
    print("\n[INFO] STEP 2.5: Verifying local data with online source...")
    if not verify_gold_data_online(latest_data):
        print("[WARN] Online data verification failed or found discrepancies. Proceeding with local data, but investigate manually.")
        # Decide if you want to abort here or just warn. For now, we warn and proceed.
        # sys.exit(1) # Uncomment to abort if online verification fails.
    
    nqy = latest_data.get("nqy", "")
    asdate = latest_data.get("asdate", "")
    
    print(f"[INFO] Latest data: nqy={nqy}, asdate={asdate}")
    
    if is_already_processed(nqy, asdate):
        print(f"[SKIP] This update has already been processed. Skipping.")
        print(f"   (nqy={nqy}, asdate={asdate})")
        sys.exit(0)
    
    print(f"[INFO] New data detected! Proceeding with workflow...")
    
    # Step 3: Generate video and image
    print("\n[INFO] STEP 3: Generating video and static image...")
    # Pass output paths as arguments to app.py
    app_args = [
        "--output_video_path", APP_OUTPUT_VIDEO_PATH,
        "--output_image_path", APP_OUTPUT_IMAGE_PATH,
        # You can add --background_theme, --custom_message, --logo_url here if needed
    ]
    if not run_script("app.py", "Video/Image Generator", *app_args):
        print("[WARN] Video/Image generation failed, but continuing...")
    
    # Step 4: Post to Blogger
    print("\n[INFO] STEP 4: Posting to Blogger...")
    if not run_script("pypost_gold.py", "Blogger Publisher"):
        print("[WARN] Blogger posting failed, but continuing...")
    
    # Step 5: Send Telegram notification
    print("\n[INFO] STEP 5: Sending Telegram notification...")
    if not run_script("telegram_notify.py", "Telegram Notifier"):
        print("[WARN] Telegram notification failed, but continuing...")
    
    # Step 6: Mark as processed
    print("\n[INFO] STEP 6: Marking as processed...")
    mark_as_processed(nqy, asdate)

    # NEW STEP 7: Post to Facebook (Image + Text only)
    print("\n[INFO] STEP 7: Posting to Facebook (Image + Text)...")
    try:
        fb_post_generator = FacebookGoldPost(data_file=os.path.join(SCRIPT_DIR, "data", "gold_prices.json"))
        if fb_post_generator.load_latest_price():
            post_text = fb_post_generator.create_post_detailed() # Use detailed post as default
            
            if post_text:
                fb_auto_post = FacebookAutoPost(config_file=os.path.join(SCRIPT_DIR, "facebook_config.json"))
                if fb_auto_post.load_config(): # Ensure config is loaded correctly
                    if os.path.exists(APP_OUTPUT_IMAGE_PATH): # Check for image file
                        print(f"[INFO] Posting image: {APP_OUTPUT_IMAGE_PATH} to Facebook...")
                        # Call facebook_auto_post.py as a subprocess for image post
                        result = subprocess.run(
                            [sys.executable, os.path.join(SCRIPT_DIR, "facebook_auto_post.py"), "--post-image", APP_OUTPUT_IMAGE_PATH, "--message", post_text],
                            capture_output=True,
                            text=True,
                            cwd=SCRIPT_DIR,
                            env=dict(os.environ, PYTHONIOENCODING="utf-8"), # Force UTF-8
                            timeout=300 # 5 minutes timeout for image upload
                        )
                        if result.returncode == 0:
                            print("[OK] Image posted to Facebook successfully!")
                            if result.stdout:
                                print(f"Facebook Post Output:\n{result.stdout}")
                        else:
                            print("[ERROR] Failed to post image to Facebook via facebook_auto_post.py.")
                            if result.stderr:
                                print(f"Facebook Post Error:\n{result.stderr}")
                            if result.stdout:
                                print(f"Facebook Post Output (if any):\n{result.stdout}")
                    else:
                        print(f"[WARN] Image file not found at {APP_OUTPUT_IMAGE_PATH}. Posting text only to Facebook...")
                        # Call facebook_auto_post.py as a subprocess for text post
                        result = subprocess.run(
                            [sys.executable, os.path.join(SCRIPT_DIR, "facebook_auto_post.py"), "--post-text", "--message", post_text],
                            capture_output=True,
                            text=True,
                            cwd=SCRIPT_DIR,
                            env=dict(os.environ, PYTHONIOENCODING="utf-8"), # Force UTF-8
                            timeout=300
                        )
                        if result.returncode == 0:
                            print("[OK] Text posted to Facebook successfully!")
                            if result.stdout:
                                print(f"Facebook Post Output:\n{result.stdout}")
                        else:
                            print("[ERROR] Failed to post text to Facebook via facebook_auto_post.py.")
                            if result.stderr:
                                print(f"Facebook Post Error:\n{result.stderr}")
                            if result.stdout:
                                print(f"Facebook Post Output (if any):\n{result.stdout}")
                else:
                    print("[ERROR] Facebook config not loaded. Cannot post to Facebook.")
            else:
                print("[ERROR] Failed to generate Facebook post text.")
        else:
            print("[ERROR] Failed to load latest gold price for Facebook post generation.")
    except Exception as e:
        print(f"[ERROR] Error during Facebook posting: {e}")

    # Summary
    print("\n" + "='*60}")
    print("  [OK] WORKFLOW COMPLETED SUCCESSFULLY")
    print("='*60}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Processed: nqy={nqy}, asdate={asdate}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)