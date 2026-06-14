from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

creds = Credentials.from_authorized_user_file("token.json", SCOPES)
print("Valid:", creds.valid)
print("Expired:", creds.expired)
print("Has refresh_token:", bool(creds.refresh_token))

if creds.expired and creds.refresh_token:
    print("Attempting refresh...")
    try:
        creds.refresh(Request())
        print("Refresh SUCCESS!")
        with open("token.json", "w") as f:
            f.write(creds.to_json())
        print("Token saved.")
    except Exception as e:
        print(f"Refresh FAILED: {e}")
elif creds.valid:
    print("Token is still valid, no refresh needed.")
else:
    print("No refresh token available - need to re-authenticate.")
