import requests
import base64
import os

key = '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'
invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-large"

# Let's test basic text-to-image first to ensure the endpoint works
payload = {
    "prompt": "A Highly detailed heavy metal concert stage with red lasers and smoke",
    "cfg_scale": 5,
    "aspect_ratio": "1:1",
    "seed": 0,
    "steps": 50
}

headers = {
    "Authorization": f"Bearer {key}",
    "Accept": "application/json"
}

print("Testing SD3 Large...")
res = requests.post(invoke_url, headers=headers, json=payload)
print(res.status_code)
if res.status_code == 200:
    print("Success text-to-image")
else:
    print(res.text)

