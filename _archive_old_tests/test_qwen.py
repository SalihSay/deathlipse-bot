import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()
# Use the user's provided key
QWEN_KEY = "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"
invoke_url = "https://ai.api.nvidia.com/v1/genai/alibaba/qwen-image-edit"
input_image_path = "assets/images/69ad33662571c7daeb009664/img_6.jpg"

print(f"Reading image from {input_image_path}...")
with open(input_image_path, "rb") as image_file:
    image_b64 = base64.b64encode(image_file.read()).decode()

image_data_url = f"data:image/jpeg;base64,{image_b64}"

prompt = "Change the background to a highly detailed heavy metal concert stage with massive black amplifier stacks, red laser lights cutting through atmospheric fog, while keeping the person and the t-shirt exactly the same."

payload = {
    "prompt": prompt,
    "image": image_data_url,
    "seed": 42
}

headers = {
    "Authorization": f"Bearer {QWEN_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("Sending request to NVIDIA Qwen-Image-Edit...")
response = requests.post(invoke_url, json=payload, headers=headers)

print(response.status_code)
if response.status_code == 200:
    result = response.json()
    if 'artifacts' in result:
        output_b64 = result['artifacts'][0]['base64']
        with open("test_qwen_result.png", "wb") as f:
            f.write(base64.b64decode(output_b64))
        print("Success! Image saved as test_qwen_result.png")
    else:
        print("No artifacts found:", result)
else:
    print("Error:", response.text)
