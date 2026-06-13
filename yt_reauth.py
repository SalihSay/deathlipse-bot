import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
credentials = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

with open("token.json", "w") as f:
    f.write(credentials.to_json())

print("Token saved to token.json successfully!")
print(f"Token valid: {credentials.valid}")
print(f"Has refresh_token: {bool(credentials.refresh_token)}")
