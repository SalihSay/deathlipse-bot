import requests
from core.config import META_ACCESS_TOKEN, META_IG_USER_ID
from core.uploader import upload_to_tmpfiles

def post(image_path, caption, product_url):
    if not META_ACCESS_TOKEN or not META_IG_USER_ID:
        print("[!] Meta API tokens missing for Threads.")
        return False
        
    image_url = upload_to_tmpfiles(image_path)
    if not image_url:
        return False
        
    print("Posting to Threads API...")
    container_url = f"https://graph.threads.net/v1.0/{META_IG_USER_ID}/threads"
    
    thread_text = f"{caption}\n\nShop now: {product_url}"
    payload = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": thread_text,
        "access_token": META_ACCESS_TOKEN
    }
    
    try:
        resp = requests.post(container_url, data=payload)
        data = resp.json()
        if "id" not in data:
            print(f"Threads Container failed: {data}")
            return False
            
        creation_id = data["id"]
        # Step 2: Publish
        publish_url = f"https://graph.threads.net/v1.0/{META_IG_USER_ID}/threads_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": META_ACCESS_TOKEN
        }
        pub_resp = requests.post(publish_url, data=publish_payload)
        pub_data = pub_resp.json()
        if "id" in pub_data:
            print(f"Threads Published! ID: {pub_data['id']}")
            return True
        else:
            print(f"Threads Publish failed: {pub_data}")
            return False
            
    except Exception as e:
        print("Threads API exception:", e)
        return False
