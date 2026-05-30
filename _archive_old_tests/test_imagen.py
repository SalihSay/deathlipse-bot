import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Test with imagen-3.0-generate-001 or imagen-3.0-generate-002
url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={GEMINI_API_KEY}"

payload = {
  "instances": [
    {"prompt": "A highly detailed heavy metal concert stage with red lasers and smoke."}
  ],
  "parameters": {
    "sampleCount": 1
  }
}

try:
    print("Requesting from Gemini Imagen 3...")
    res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
    print(res.status_code)
    if res.status_code == 200:
        data = res.json()
        print("Success! Keys:", data.keys())
    else:
        print("Error:", res.text)
except Exception as e:
    print("Exception:", e)
