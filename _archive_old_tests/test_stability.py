import requests
import os

api_key = "sk-CJJTIPiDSzoHR6pmvWLbJZ5026rZI2RGqWiujNl3uB71wzbP"

# First, let's check the user's balance
response = requests.get(
    "https://api.stability.ai/v1/user/balance",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)

print("Balance Check:")
print(response.status_code)
print(response.json() if response.status_code == 200 else response.text)

# Check available engines
response = requests.get(
    "https://api.stability.ai/v1/engines/list",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)
if response.status_code == 200:
    engines = response.json()
    print("\nAvailable Engines:")
    for engine in engines:
        print(f"- {engine['id']} ({engine['type']})")
else:
    print(f"\nFailed to get engines: {response.text}")
