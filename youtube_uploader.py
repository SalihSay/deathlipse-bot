import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"

def get_authenticated_service():
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"[!] {CLIENT_SECRETS_FILE} not found. YouTube upload will fail.")
                return None
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=0)
            
        with open("token.json", "w") as token_file:
            token_file.write(credentials.to_json())
            
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video_to_shorts(video_path, title, description, tags=None):
    youtube = get_authenticated_service()
    if not youtube:
        return False
        
    if tags is None:
        tags = ["deathlipse", "metal", "goth", "altfashion", "streetwear"]
        
    # Shorts typically requires #shorts in title or description to be categorized properly
    if "#shorts" not in description.lower() and "#shorts" not in title.lower():
        description += "\n\n#shorts"
        
    request_body = {
        "snippet": {
            "categoryId": "22", # People & Blogs or Film & Animation. 22 is People & Blogs. Let's use 22 or 26 (How-to & Style). 26 is probably better for clothing.
            "title": title[:100], # Max 100 chars
            "description": description[:5000],
            "tags": tags[:15] # YouTube limits tags
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    request_body["snippet"]["categoryId"] = "26"

    media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )
    
    try:
        response = request.execute()
        print(f"YouTube Shorts Uploaded! Video ID: {response['id']}")
        return True
    except googleapiclient.errors.HttpError as e:
        print(f"YouTube Upload Failed: {e}")
        return False
    except Exception as e:
        print(f"YouTube General Error: {e}")
        return False
