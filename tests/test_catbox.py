import requests
import os
from dotenv import load_dotenv

load_dotenv()
AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY")

with open("dummy.png", "rb") as f:
    resp = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f})
    link = resp.text
    print("catbox link:", link)

url = "https://app.ayrshare.com/api/post"
headers = {
    "Authorization": f"Bearer {AYRSHARE_API_KEY}",
    "Content-Type": "application/json"
}

# Test Pinterest with image
payload = {
    "post": "Test catbox image",
    "platforms": ["pinterest"],
    "mediaUrls": [link]
}
print("\nPinterest catbox test:")
resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.text)

