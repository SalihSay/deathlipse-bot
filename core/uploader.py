import requests

def upload_to_tmpfiles(file_path):
    print(f"Uploading to tmpfiles.org: {file_path}")
    url = "https://tmpfiles.org/api/v1/upload"
    with open(file_path, "rb") as f:
        files = {"file": f}
        try:
            resp = requests.post(url, files=files)
            data = resp.json()
            if data.get("status") == "success":
                file_url = data["data"]["url"]
                direct_url = file_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                return direct_url
            print(f"Upload failed. Response: {data}")
        except Exception as e:
            print("Upload exception:", e)
    return None
