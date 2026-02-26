import os
import sys
import subprocess

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths for the image and config
IMAGE_PATH = os.path.join(SCRIPT_DIR, "out", "output_panel.jpg")
FB_AUTO_POST_SCRIPT = os.path.join(SCRIPT_DIR, "facebook_auto_post.py")

def run_test_image_post():
    print("[INFO] Attempting to send a test image post to Facebook.")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"[ERROR] ไม่พบไฟล์รูปภาพ: {IMAGE_PATH}. โปรดตรวจสอบว่า main_workflow.py สร้างไฟล์นี้แล้ว")
        return False

    test_message = "นี่คือโพสต์ทดสอบภาพนิ่งจากระบบ OpenClaw Gold Price Generator ครับ"
    print(f"[INFO] Test message: {test_message}")
    print(f"[INFO] Using image: {IMAGE_PATH}")
    
    try:
        # Call facebook_auto_post.py as a subprocess
        result = subprocess.run(
            [sys.executable, FB_AUTO_POST_SCRIPT, "--post-image", IMAGE_PATH, "--message", test_message],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"), # Force UTF-8
            timeout=300 # 5 minutes timeout for image upload
        )
        
        if result.returncode == 0:
            print("[OK] Test image post process completed successfully.")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
            return True
        else:
            print("[ERROR] Test image post process failed.")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
            if result.stdout:
                print(f"Output (if any):\n{result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Test image post timed out.")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    run_test_image_post()
