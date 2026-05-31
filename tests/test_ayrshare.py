import os
import requests
from dotenv import load_dotenv

load_dotenv()
AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY")

url = "https://app.ayrshare.com/api/post"
headers = {
    "Authorization": f"Bearer {AYRSHARE_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "post": "Test post for Ayrshare",
    "platforms": ["instagram"],
    "mediaUrls": ["https://tmpfiles.org/dl/12345/test.jpg"]
}
print("Instagram test:")
resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.text)

payload["platforms"] = ["tiktok"]
print("\nTikTok test:")
resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.text)

payload["platforms"] = ["pinterest"]
print("\nPinterest test:")
resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.text)

