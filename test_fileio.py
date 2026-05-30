import requests
import os
from dotenv import load_dotenv

load_dotenv()
AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY")

# Create a small dummy image
with open("dummy.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0aIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

# Upload to file.io
with open("dummy.png", "rb") as f:
    resp = requests.post("https://file.io", files={"file": f})
    data = resp.json()
    link = data.get("link")
    print("file.io link:", link)

url = "https://app.ayrshare.com/api/post"
headers = {
    "Authorization": f"Bearer {AYRSHARE_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "post": "Test file.io image",
    "platforms": ["pinterest"],
    "mediaUrls": [link]
}
print("\nPinterest file.io test:")
resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.text)

