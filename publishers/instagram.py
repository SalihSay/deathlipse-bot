import asyncio
import requests
from core.config import META_ACCESS_TOKEN, META_IG_USER_ID
from core.uploader import upload_to_tmpfiles

def post_story(story_image_path, product_url):
    if not META_ACCESS_TOKEN or not META_IG_USER_ID:
        print("[!] Meta API tokens missing.")
        return False
        
    image_url = upload_to_tmpfiles(story_image_path)
    if not image_url:
        return False
        
    print("Posting Story to Meta Graph API...")
    # Step 1: Create Container
    container_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "media_type": "STORIES",
        "access_token": META_ACCESS_TOKEN
    }
    
    # Story link sticker parameter is strictly NOT supported by Instagram Graph API
    # so we rely on "Link in Bio" text instead.
    
    try:
        resp = requests.post(container_url, data=payload)
        data = resp.json()
        if "id" not in data:
            print(f"Container failed: {data}")
            return False
            
        creation_id = data["id"]
        # Step 2: Publish
        publish_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": META_ACCESS_TOKEN
        }
        pub_resp = requests.post(publish_url, data=publish_payload)
        pub_data = pub_resp.json()
        if "id" in pub_data:
            print(f"Meta Graph Story Published! ID: {pub_data['id']}")
            return True
        else:
            print(f"Publish failed: {pub_data}")
            return False
            
    except Exception as e:
        print("Meta Graph API exception:", e)
        return False

async def post_reels(video_path, caption):
    if not META_ACCESS_TOKEN or not META_IG_USER_ID:
        print("[!] Meta API tokens missing for Reels.")
        return False
        
    video_url = upload_to_tmpfiles(video_path)
    if not video_url:
        return False
        
    print("Posting Reels to Meta Graph API...")
    container_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true",
        "access_token": META_ACCESS_TOKEN
    }
    
    try:
        resp = requests.post(container_url, data=payload)
        data = resp.json()
        if "id" not in data:
            print(f"Reels Container failed: {data}")
            return False
            
        creation_id = data["id"]
        
        # Polling for processing completion
        status_url = f"https://graph.facebook.com/v19.0/{creation_id}?fields=status_code&access_token={META_ACCESS_TOKEN}"
        for _ in range(24):  # Max 240 seconds
            status_resp = requests.get(status_url)
            status_data = status_resp.json()
            if status_data.get("status_code") == "FINISHED":
                break
            elif status_data.get("status_code") == "ERROR":
                print(f"Reels processing error: {status_data}")
                return False
            await asyncio.sleep(10)
            
        # Publish
        publish_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": META_ACCESS_TOKEN
        }
        pub_resp = requests.post(publish_url, data=publish_payload)
        pub_data = pub_resp.json()
        if "id" in pub_data:
            print(f"Meta Graph Reels Published! ID: {pub_data['id']}")
            return True
        else:
            print(f"Reels Publish failed: {pub_data}")
            return False
    except Exception as e:
        print("Meta Reels exception:", e)
        return False
