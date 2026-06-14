import requests
from core.config import ZERNIO_API_KEY
from core.uploader import upload_to_tmpfiles

def post(text, media_path, platforms_config, media_type="video"):
    if not ZERNIO_API_KEY:
        return False
        
    media_url = upload_to_tmpfiles(media_path)
    if not media_url:
        return False
        
    url = "https://zernio.com/api/v1/posts"
    headers = {
        "Authorization": f"Bearer {ZERNIO_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": text,
        "platforms": platforms_config,
        "mediaItems": [{"type": media_type, "url": media_url}],
        "publishNow": True
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            return True
        print(f"Zernio post failed: {resp.text}")
    except Exception as e:
        print("Zernio API exception:", e)
    return False
