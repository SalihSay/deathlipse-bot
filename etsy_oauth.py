"""
Etsy OAuth 2.0 PKCE Token Generator
Tarayıcıda Etsy'ye giriş yapıp izin verdikten sonra otomatik olarak token alır.
"""
import hashlib
import base64
import os
import secrets
import webbrowser
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

ETSY_API_KEY = "gqnem32usqjmqjaeg0adl0ly"
REDIRECT_URI = "http://localhost:3000/callback"
SCOPES = "listings_r listings_w shops_r"

# PKCE code verifier & challenge
code_verifier = secrets.token_urlsafe(64)[:128]
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip("=")

state = secrets.token_urlsafe(16)

auth_code_received = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code_received
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if "code" in params:
            auth_code_received = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Basarili! Bu sekmeyi kapatabilirsin.</h1></body></html>")
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            error = params.get("error", ["unknown"])[0]
            self.wfile.write(f"<html><body><h1>Hata: {error}</h1></body></html>".encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def main():
    # Build authorization URL
    auth_url = (
        f"https://www.etsy.com/oauth/connect"
        f"?response_type=code"
        f"&client_id={ETSY_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES.replace(' ', '%20')}"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    
    print("=" * 60)
    print("ETSY OAuth 2.0 Token Generator")
    print("=" * 60)
    print("\nTarayici aciliyor... Etsy'ye giris yap ve izin ver.\n")
    print("Eger tarayici acilmazsa bu linki manuel olarak ac:")
    print(auth_url)
    print("\nBekleniyor...\n")
    
    webbrowser.open(auth_url)
    
    # Start local server to catch callback
    server = HTTPServer(("localhost", 3000), CallbackHandler)
    server.timeout = 300  # 5 minute timeout
    
    while auth_code_received is None:
        server.handle_request()
    
    server.server_close()
    
    print("Authorization code alindi! Token alinıyor...")
    
    # Exchange code for token
    token_url = "https://api.etsy.com/v3/public/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": ETSY_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": auth_code_received,
        "code_verifier": code_verifier,
    }
    
    resp = requests.post(token_url, data=token_data)
    
    if resp.status_code == 200:
        token_info = resp.json()
        access_token = token_info["access_token"]
        refresh_token = token_info.get("refresh_token", "")
        
        print("\n" + "=" * 60)
        print("TOKEN BASARIYLA ALINDI!")
        print("=" * 60)
        print(f"Access Token: {access_token[:20]}...")
        print(f"Refresh Token: {refresh_token[:20]}...")
        
        # Save to .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        
        # Read existing .env
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                env_lines = f.readlines()
        
        # Remove old Etsy token lines if any
        env_lines = [l for l in env_lines if not l.startswith("ETSY_ACCESS_TOKEN=") and not l.startswith("ETSY_REFRESH_TOKEN=")]
        
        # Add new tokens
        env_lines.append(f"\nETSY_ACCESS_TOKEN={access_token}\n")
        env_lines.append(f"ETSY_REFRESH_TOKEN={refresh_token}\n")
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(env_lines)
        
        # Also save to a JSON file for easy access
        with open("etsy_token.json", "w") as f:
            json.dump(token_info, f, indent=2)
        
        print(f"\nToken .env dosyasina ve etsy_token.json'a kaydedildi!")
        print("Artik bu pencereyi kapatabilirsin.")
    else:
        print(f"\nHATA: Token alinamadi!")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

if __name__ == "__main__":
    main()
