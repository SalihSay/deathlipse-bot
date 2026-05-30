import os
import csv
import sys
import requests
from dotenv import load_dotenv
import subprocess
import time

load_dotenv()
AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY")

CSV_FILE = "bulk_schedule.csv"

def open_media(media_path):
    """İlgili videoyu veya resmi işletim sisteminin varsayılan uygulamasında açar."""
    abs_path = os.path.abspath(media_path)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.call(["open", abs_path])
    else:
        subprocess.call(["xdg-open", abs_path])

def upload_local_media_to_ayrshare(file_path):
    """Ayrshare'e yerel dosya yüklemek için gereken medya endpointi."""
    if not AYRSHARE_API_KEY:
        return "SIMULATED_URL"
        
    # Gerçek Ayrshare Media Upload Endpoint'i
    url = "https://app.ayrshare.com/api/media"
    headers = {"Authorization": f"Bearer {AYRSHARE_API_KEY}"}
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        try:
            resp = requests.post(url, headers=headers, files=files)
            if resp.status_code == 200:
                return resp.json().get("url")
        except Exception as e:
            print("Media upload failed:", e)
    return None

def post_to_ayrshare(text, media_path, platforms):
    """İçeriği Ayrshare aracılığıyla Instagram, TikTok veya Pinterest'e fırlatır."""
    if not AYRSHARE_API_KEY:
        print("[!] AYRSHARE_API_KEY bulunamadı. (.env dosyasında yok)")
        print(f"[!] SİMÜLASYON MODU: {platforms} platformlarına gönderilmiş gibi yapılıyor...")
        time.sleep(1)
        return True
        
    print(f"-> {media_path} sunucuya yükleniyor...")
    media_url = upload_local_media_to_ayrshare(media_path)
    if not media_url:
        print("-> Video/Resim sunucuya yüklenemedi!")
        return False
        
    url = "https://app.ayrshare.com/api/post"
    headers = {
        "Authorization": f"Bearer {AYRSHARE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "post": text,
        "platforms": platforms,
        "mediaUrls": [media_url]
    }
    
    print(f"-> {platforms} platformlarına yayın isteği gönderiliyor...")
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            print(f"-> Başarıyla yayınlandı: {platforms}")
            return True
        else:
            print("-> Ayrshare API Hatası:", resp.text)
            return False
    except Exception as e:
        print("-> İstek başarısız oldu:", e)
        return False

def main():
    print("=== HUMAN-IN-THE-LOOP SOCIAL PUBLISHER (MANUEL ONAY SİSTEMİ) ===")
    if not os.path.isfile(CSV_FILE):
        print(f"Hata: {CSV_FILE} bulunamadı.")
        return
        
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        
    if len(reader) <= 1:
        print("CSV dosyasında hiç gönderi yok.")
        return
        
    header = reader[0]
    if "Status" not in header:
        header.append("Status")
        
    modified = False
    
    for i in range(1, len(reader)):
        row = reader[i]
        
        while len(row) < len(header):
            row.append("PENDING")
            
        status = row[5]
        if status in ["PUBLISHED", "SKIPPED"]:
            continue
            
        ig_text = row[0]
        pin_text = row[1]
        img_file = f"bulk_images/{row[2]}"
        vid_file = f"reels_output/{row[3]}"
        
        print("\n" + "="*60)
        print(f" YAYIN BEKLEYEN GÖNDERİ #{i}")
        print("="*60)
        print("[Instagram & TikTok Metni]:\n")
        print(ig_text)
        print("\n[Pinterest Metni]:\n")
        print(pin_text)
        print("\n[Medya Dosyaları]:")
        print(f" - Resim: {img_file}")
        print(f" - Video: {vid_file}")
        
        print("\n-> İncelenmesi için video ve görsel ekranda açılıyor...")
        try:
            if os.path.exists(img_file): open_media(img_file)
            if os.path.exists(vid_file): open_media(vid_file)
        except Exception as e:
            print(f"Görseller otomatik açılamadı: {e}")
            
        print("\n[ONAY İŞLEMİ]")
        print(" y = Onaylıyorum, platformlarda paylaş (Publish)")
        print(" s = Atla, bunu asla paylaşma (Skip)")
        print(" q = Programdan çık (Quit)")
        action = input("Seçiminiz: ").strip().lower()
        
        if action == 'q':
            print("Programdan çıkılıyor...")
            break
        elif action == 's':
            row[5] = "SKIPPED"
            modified = True
            print("-> Gönderi atlandı (Skipped).")
        elif action == 'y':
            print("\n>>> ONAY ALINDI. YAYIN SÜRECİ BAŞLIYOR <<<")
            
            # 1. Instagram Reels ve TikTok (Video)
            success_ig_tiktok = post_to_ayrshare(ig_text, vid_file, ["tiktok", "instagram"])
            
            # 2. Pinterest (Resim)
            success_pin = post_to_ayrshare(pin_text, img_file, ["pinterest"])
            
            if success_ig_tiktok and success_pin:
                row[5] = "PUBLISHED"
                modified = True
                print("\n-> Tüm platformlarda başarıyla yayımlandı!")
            else:
                print("\n-> Yayınlanırken hata oluştu. Durum 'PENDING' olarak bırakılıyor.")
                break
        else:
            print("Geçersiz giriş. Durum PENDING olarak bırakılıyor.")
            break
            
    if modified:
        with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for r in reader[1:]:
                writer.writerow(r)
        print("\n-> CSV kayıtları (Status) başarıyla güncellendi.")
        
    print("\nTüm işlemler tamamlandı.")

if __name__ == "__main__":
    main()
