import os
import sys

# Get the directory of the current script (temp_facebook_test.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR) # Ensure local modules are found

from facebook_auto_post import FacebookAutoPost

def run_test_post():
    print("[INFO] Attempting to send a test text post to Facebook.")
    fb_auto_post = FacebookAutoPost(config_file=os.path.join(SCRIPT_DIR, "facebook_config.json"))
    
    if not fb_auto_post.load_config():
        print("[ERROR] Failed to load Facebook config. Aborting test post.")
        return False
    
    test_message = "นี่คือโพสต์ทดสอบจากระบบ OpenClaw Gold Price Generator ครับ"
    print(f"[INFO] Test message: {test_message}")
    
    if fb_auto_post.post_to_facebook(test_message):
        print("[OK] Test post sent successfully!")
        return True
    else:
        print("[ERROR] Failed to send test post.")
        return False

if __name__ == "__main__":
    # Force UTF-8 for this script's output
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception as e:
        print(f"[WARN] Could not reconfigure stdout/stderr for UTF-8: {e}")

    run_test_post()
