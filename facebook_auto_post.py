import json
import requests
import os
from pathlib import Path
import argparse

# --- Configuration --- #
API_VERSION = "v21.0"

class FacebookAutoPost:
    def __init__(self, config_file="facebook_config.json"):
        self.config_file = config_file
        self.user_access_token = None
        self.page_id = None
        self.page_access_token = None
        self.target_page_name = None
        self.load_config()

    def load_config(self):
        """โหลดการตั้งค่า Facebook API และพยายามดึง Page Token"""
        print(f"[DEBUG] Current Working Directory: {os.getcwd()}") # Debug Print
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_absolute_path = os.path.abspath(os.path.join(script_dir, self.config_file)) # Ensure absolute path relative to script
        print(f"[DEBUG] Absolute Path ของ config file: {config_absolute_path}") # Debug Print

        if not os.path.exists(config_absolute_path):
            print(f"[WARN] ไม่พบไฟล์ config ที่: {config_absolute_path}")
            print("[INFO] กำลังสร้างไฟล์ตัวอย่าง...")
            self._create_sample_config()
            return False

        try:
            with open(config_absolute_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"[DEBUG] โหลด config สำเร็จ: {config}") # Debug Print
                self.user_access_token = config.get('user_access_token') # ใช้ user_access_token
                self.target_page_name = config.get('target_page_name')
                
                print(f"[DEBUG] user_access_token: {self.user_access_token[:10] if self.user_access_token else 'None'}...") # Debug Print
                print(f"[DEBUG] target_page_name: {self.target_page_name}") # Debug Print
                
                if not self.user_access_token or not self.target_page_name:
                    print("[WARN] กรุณาตั้งค่า user_access_token และ target_page_name ในไฟล์ config")
                    return False

                # ตรวจสอบสิทธิ์ของ User Token
                if not self._check_token_permissions(self.user_access_token):
                    print("[ERROR] User Access Token ไม่มีสิทธิ์เพียงพอ. โปรดแก้ไข.")
                    return False

                # ดึง Page ID และ Page Access Token
                page_id, page_access_token = self._get_specific_page_token(self.user_access_token, self.target_page_name)
                if page_id and page_access_token:
                    self.page_id = page_id
                    self.page_access_token = page_access_token
                    print(f"[OK] ได้ Page ID: {self.page_id} และ Page Token แล้ว")
                    return True
                else:
                    print(f"[ERROR] ไม่สามารถดึง Page Token สำหรับเพจ '{self.target_page_name}' ได้")
                    return False

        except json.JSONDecodeError as e:
            print(f"[ERROR] ไฟล์ {self.config_file} มีรูปแบบ JSON ไม่ถูกต้อง: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] เกิดข้อผิดพลาดในการโหลด config หรือดึง Page Token: {e}")
            return False

    def _create_sample_config(self):
        """สร้างไฟล์ config ตัวอย่าง"""
        sample_config = {
            "user_access_token": "YOUR_USER_ACCESS_TOKEN_HERE",
            "target_page_name": "YOUR_TARGET_PAGE_NAME_HERE",
            "instructions": {
                "how_to_get_user_access_token": [
                    "1. ไปที่ https://developers.facebook.com/",
                    "2. สร้าง App ใหม่ หรือใช้ App ที่มีอยู่",
                    "3. ไปที่ Tools > Graph API Explorer",
                    "4. เลือก User/Page ที่ต้องการ (เป็นตัวคุณก่อน)",
                    "5. เลือก permissions: pages_manage_posts, pages_read_engagement, public_profile",
                    "6. Generate Access Token (อันนี้คือ User Access Token ยาวๆ)",
                    "7. คัดลอก User Access Token มาใส่ที่นี่ (user_access_token)"
                ],
                "how_to_get_page_name": [
                    "1. ใส่ชื่อเพจของคุณให้ตรงเป๊ะกับบน Facebook",
                    "2. เช่น \"ราคา ทองคำ วันนี้\""
                ]
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, ensure_ascii=False, indent=2)
            print(f"[OK] สร้างไฟล์ {self.config_file} แล้ว")
            print("[INFO] กรุณาแก้ไขไฟล์และใส่ user_access_token และ target_page_name ของคุณ")
        except Exception as e:
            print(f"[ERROR] ไม่สามารถสร้างไฟล์: {e}")

    def _check_token_permissions(self, token):
        """ตรวจสอบว่า Token นี้มีสิทธิ์อะไรบ้าง"""
        url = f"https://graph.facebook.com/{API_VERSION}/me/permissions"
        params = {'access_token': token}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if 'data' in data:
                print(f"🧐 สิทธิ์ที่มีใน User Token นี้:")
                permissions = [p['permission'] for p in data['data'] if p['status'] == 'granted']
                print(permissions)
                required = ['pages_manage_posts', 'pages_read_engagement']
                missing = [req for req in required if req not in permissions]
                if missing:
                    print(f"❌ ขาดสิทธิ์สำคัญ: {missing}")
                    print("👉 กรุณาไปที่ Graph API Explorer > Add Permissions > เลือกสิทธิ์ที่ขาด > กด Generate Token ใหม่")
                    return False
                else:
                    print("✅ สิทธิ์ User Token ครบถ้วน!")
                    return True
            else:
                print("❌ User Token ไม่ถูกต้อง ตรวจสอบไม่ได้")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] เกิดข้อผิดพลาดในการตรวจสอบสิทธิ์ User Token: {e}")
            return False

    def _get_specific_page_token(self, user_token, page_name_query):
        """ดึง Page Token โดยค้นหาจากรายชื่อเพจทั้งหมด (/me/accounts)"""
        url = f"https://graph.facebook.com/{API_VERSION}/me/accounts"
        params = {
            'access_token': user_token,
            'limit': 100 # ดึงมา 100 เพจแรก
        }
        print(f"\n[INFO] กำลังค้นหาเพจ '{page_name_query}' และขอ Page Token...")
        try:
            while True:
                response = requests.get(url, params=params)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                if 'error' in data:
                    print(f"[ERROR] Error ในการดึงรายชื่อเพจ: {data['error']['message']}")
                    return None, None

                for page in data.get('data', []):
                    if page.get('name') == page_name_query:
                        # เจอเพจแล้ว! ส่งคืน ID และ Access Token ของเพจนั้น
                        return page.get('id'), page.get('access_token')
                
                # จัดการ Pagination (ถ้ามีเพจเยอะเกิน 100)
                if 'paging' in data and 'next' in data['paging']:
                    url = data['paging']['next']
                    params = {} # ล้าง params เพราะ url next มีมาให้แล้ว
                else:
                    break # ไม่มีเพจเพิ่มเติมแล้ว
            print(f"[ERROR] หาเพจ '{page_name_query}' ไม่เจอ หรือ User Token นี้ไม่มีสิทธิ์แอดมินในเพจนั้น")
            return None, None
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] เกิดข้อผิดพลาดในการดึง Page Token: {e}")
            return None, None

    def post_to_facebook(self, message):
        """โพสต์ข้อความไปยัง Facebook Page"""
        if not self.page_access_token or not self.page_id:
            print("[ERROR] กรุณาตั้งค่า Facebook API หรือดึง Page Token ให้สำเร็จก่อน")
            return False
        
        url = f"https://graph.facebook.com/{API_VERSION}/{self.page_id}/feed"
        
        payload = {
            'message': message,
            'access_token': self.page_access_token # ⚠️ ใช้ Page Access Token
        }
        
        try:
            print("[INFO] กำลังโพสต์ข้อความไปยัง Facebook...")
            response = requests.post(url, data=payload)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                print(f"[OK] โพสต์สำเร็จ! Post ID: {post_id}")
                return True
            else:
                print(f"[ERROR] โพสต์ไม่สำเร็จ: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] เกิดข้อผิดพลาด: {e}")
            return False
    
    def post_with_image(self, message, image_path):
        """โพสต์พร้อมรูปภาพ"""
        if not self.page_access_token or not self.page_id:
            print("[ERROR] กรุณาตั้งค่า Facebook API หรือดึง Page Token ให้สำเร็จก่อน")
            return False
        
        if not os.path.exists(image_path):
            print(f"[ERROR] ไม่พบไฟล์รูปภาพ: {image_path}")
            return False

        url = f"https://graph.facebook.com/{API_VERSION}/{self.page_id}/photos"
        
        try:
            with open(image_path, 'rb') as image_file:
                payload = {
                    'message': message,
                    'access_token': self.page_access_token # ⚠️ ใช้ Page Access Token
                }
                files = {
                    'source': image_file
                }
                
                print("[INFO] กำลังโพสต์พร้อมรูปภาพไปยัง Facebook...")
                response = requests.post(url, data=payload, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    post_id = result.get('id')
                    print(f"[OK] โพสต์สำเร็จ! Post ID: {post_id}")
                    return True
                else:
                    print(f"[ERROR] โพสต์ไม่สำเร็จ: {response.status_code}")
                    print(f"Error: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] เกิดข้อผิดพลาด: {e}")
            return False
    
    def post_with_video(self, message, video_path):
        """โพสต์พร้อมวิดีโอ"""
        if not self.page_access_token or not self.page_id:
            print("[ERROR] กรุณาตั้งค่า Facebook API หรือดึง Page Token ให้สำเร็จก่อน")
            return False
        
        if not os.path.exists(video_path):
            print(f"[ERROR] ไม่พบไฟล์วิดีโอ: {video_path}")
            return False

        url = f"https://graph.facebook.com/{API_VERSION}/{self.page_id}/videos"
        
        try:
            with open(video_path, 'rb') as video_file:
                payload = {
                    'description': message,
                    'access_token': self.page_access_token # ⚠️ ใช้ Page Access Token
                }
                files = {
                    'source': video_file
                }
                
                print("[INFO] กำลังอัพโหลดวิดีโอไปยัง Facebook...")
                print("[WAIT] กรุณารอสักครู่ (อาจใช้เวลาหลายนาที)...")
                response = requests.post(url, data=payload, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    video_id = result.get('id')
                    print(f"[OK] โพสต์วิดีโอสำเร็จ! Video ID: {video_id}")
                    return True
                else:
                    print(f"[ERROR] โพสต์ไม่สำเร็จ: {response.status_code}")
                    print(f"Error: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] เกิดข้อผิดพลาด: {e}")
            return False

def main():
    """ฟังก์ชันหลัก"""
    parser = argparse.ArgumentParser(description="Facebook Auto Post for Gold Price.")
    parser.add_argument("--post-text", action="store_true", help="Post as text only.")
    parser.add_argument("--post-image", type=str, help="Path to image file to post.")
    parser.add_argument("--post-video", type=str, help="Path to video file to post.")
    parser.add_argument("--message", type=str, help="Message for the post.")
    
    # Removed --post-type as it was for generating text in old facebook_post.py
    args = parser.parse_args()

    # สร้าง instance
    fb_auto_post = FacebookAutoPost()
    
    # ตรวจสอบว่าโหลด config และได้ page token สำเร็จหรือไม่
    if not fb_auto_post.page_access_token:
        print("[ERROR] ไม่สามารถดำเนินการต่อได้ เนื่องจากไม่มี Page Access Token ที่ถูกต้อง.")
        return

    post_message = args.message
    if not post_message:
        print("[ERROR] ต้องระบุข้อความ (--message) สำหรับการโพสต์.")
        return

    if args.post_image:
        fb_auto_post.post_with_image(post_message, args.post_image)
    elif args.post_video:
        fb_auto_post.post_with_video(post_message, args.post_video)
    elif args.post_text:
        fb_auto_post.post_to_facebook(post_message)
    else:
        print("[ERROR] ไม่ได้ระบุ action ที่ชัดเจนสำหรับการโพสต์ (เช่น --post-text, --post-video, หรือ --post-image).")

    print("\n[OK] Facebook Auto Post Workflow Completed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Workflow interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error in facebook_auto_post.py: {e}")
        import traceback
        traceback.print_exc()