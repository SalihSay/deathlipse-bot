import os
import requests
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

print("Requesting from HF...")
image_bytes = query({
    "inputs": "An atmospheric dark Gothic alleyway at night. Wet cobblestones reflecting bright red and purple neon lights from a vintage bar sign. Heavy metal grunge aesthetic, thick smoke, moody dramatic shadows, intricate details, 8k resolution, highly detailed photography",
})

try:
    image = Image.open(io.BytesIO(image_bytes))
    image.save("hf_test.png")
    print("Success!")
except Exception as e:
    print("Error:", e, image_bytes)
