import requests
import base64
import json
import sys

API_KEY = "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"
invoke_url = "https://ai.api.nvidia.com/v1/cv/alibaba/qwen-image-edit"

def get_b64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Let's see if there is an image to test with
image_path = "model_nobg.png"

try:
    image_b64 = get_b64(image_path)
except Exception as e:
    print(f"Error reading image: {e}")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

payload = {
    "prompt": "Change the shirt to a black heavy metal t-shirt",
    "image": f"data:image/png;base64,{image_b64}",
    "seed": 42
}

print("Gönderiliyor...")
response = requests.post(invoke_url, headers=headers, json=payload)

if response.status_code == 200:
    print("Başarılı!")
    data = response.json()
    # Usually in data['artifacts'][0]['base64'] or similar
    try:
        import pprint
        print("Response keys:", data.keys())
    except:
        pass
else:
    print(f"Hata: {response.status_code}")
    print(response.text)
