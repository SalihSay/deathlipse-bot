import requests

url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}
payload = {
    "model": "meta/llama-4-maverick-17b-128e-instruct",
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 10
}

try:
    print("Sending request...")
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print("Status code:", response.status_code)
    print("Response body:", response.text)
except Exception as e:
    print("Error:", e)
