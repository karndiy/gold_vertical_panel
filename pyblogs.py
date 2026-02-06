
# 8971911068975230651 smsgoldthai
# 3446448090281641814 goallike

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Blogger API Scopes
SCOPES = ['https://www.googleapis.com/auth/blogger']

# --- CONFIGURATION ---
TARGET_BLOG_ID = "8971911068975230651"  # ราคาทองคำ Blog
# ---------------------

def get_service():
    """Authenticates the user and returns the Blogger service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('blogger', 'v3', credentials=creds)

def post_to_blogger(service, blog_id, title, content, labels=[]):
    """Publishes a post to the specific Blog ID."""
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": labels
    }
    
    try:
        print(f"Attempting to post to Blog ID: {blog_id}...")
        request = service.posts().insert(blogId=blog_id, body=body)
        response = request.execute()
        print("-" * 30)
        print("Success! Post Published.")
        print(f"Title: {response.get('title')}")
        print(f"URL:   {response.get('url')}")
        print("-" * 30)
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == '__main__':
    # 1. Login
    blogger_service = get_service()

    # 2. Prepare your content
    # You can use HTML tags like <b>, <i>, <h1>, <br>, etc.
    my_title = "อัปเดตราคาทองคำวันนี้"
    my_content = """
    <h3>รายงานราคาทองคำประจำวัน</h3>
    <p>นี่คือโพสต์ที่สร้างโดยระบบอัตโนมัติผ่าน Python API</p>
    <ul>
        <li>ราคาทองแท่ง: 4x,xxx บาท</li>
        <li>วันที่: 04/02/2026</li>
    </ul>
    <p>ติดตามข่าวสารได้ที่หน้าเว็บหลักครับ</p>
    """
    my_labels = ["ราคาทอง", "PythonAuto", "GoldPrice"]

    # 3. Execute the post
    post_to_blogger(blogger_service, TARGET_BLOG_ID, my_title, my_content, my_labels)