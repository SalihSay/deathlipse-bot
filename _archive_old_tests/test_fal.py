import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
FAL_KEY = os.getenv("FAL_API_KEY")

url = "https://fal.run/fal-ai/flux/dev"
headers = {
    "Authorization": f"Key {FAL_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "prompt": "A highly detailed heavy metal concert stage. Massive black amplifier stacks in the background, vibrant piercing red laser lights cutting through thick atmospheric fog. Epic rock and roll atmosphere, 8k resolution, photorealistic",
    "image_size": "square_hd",
    "num_inference_steps": 28,
    "guidance_scale": 3.5,
    "sync_mode": True
}

try:
    print("Requesting from Fal.ai...")
    res = requests.post(url, headers=headers, json=payload, timeout=60)
    print(res.status_code)
    if res.status_code == 200:
        data = res.json()
        print("Success! Image URL:", data.get('images', [{}])[0].get('url'))
    else:
        print("Error:", res.text)
except Exception as e:
    print("Exception:", e)
