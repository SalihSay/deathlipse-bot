import requests
import os

key = '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'
url = 'https://integrate.api.nvidia.com/v1/images/edits'

image_path = "assets/images/69ad33662571c7daeb009664/img_6.jpg"

headers = {
    'Authorization': f'Bearer {key}',
    'Accept': 'application/json'
}

data = {
    "model": "qwen-image-edit",
    "prompt": "Change the background to a highly detailed heavy metal concert stage, while keeping the person and the t-shirt exactly the same."
}

files = {
    "image": ("image.jpg", open(image_path, "rb"), "image/jpeg")
}

print("Testing OpenAI format...")
res = requests.post(url, headers=headers, data=data, files=files)
print(res.status_code)
if res.status_code == 200:
    print(res.json())
else:
    print(res.text)
