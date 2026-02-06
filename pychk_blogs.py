import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Permissions for reading and writing to Blogger
SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_service():
    """Handles OAuth2 authentication and returns the Blogger service object."""
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

def list_blogs(service):
    """Fetches and prints all blogs associated with the account."""
    print("\n--- Fetching your Blog IDs ---")
    results = service.blogs().listByUser(userId='self').execute()
    
    if 'items' in results:
        for blog in results['items']:
            print(f"Name: {blog['name']}")
            print(f"ID:   {blog['id']}")
            print(f"URL:  {blog['url']}\n" + "-"*30)
        return results['items'][0]['id'] # Returns the first blog ID as a default
    else:
        print("No blogs found.")
        return None

def create_post(service, blog_id, title, content, tags=[]):
    """Creates a new post on the specified blog."""
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": tags
    }
    
    try:
        request = service.posts().insert(blogId=blog_id, body=body)
        response = request.execute()
        print(f"Successfully posted!")
        print(f"Post Link: {response.get('url')}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # 1. Initialize the API
    service = get_service()

    # 2. List all blogs and get the first ID automatically
    # (Or manually replace target_blog_id with your specific ID)
    target_blog_id = list_blogs(service)

    if target_blog_id:
        print(f"Ready to post to Blog ID: {target_blog_id}")
        
        # 3. Create a post
        title = "My First Automated Post"
        content = """
        <h2>Welcome to my Blog</h2>
        <p>This post was created using <b>Python</b> and the Blogger API v3.</p>
        <p>Current Year: 2026</p>
        """
        tags = ["Python", "Automation", "Tech"]
        
        # Ask for confirmation before posting
        confirm = input("Do you want to publish this post? (y/n): ")
        if confirm.lower() == 'y':
            create_post(service, target_blog_id, title, content, tags)
        else:
            print("Post cancelled.")