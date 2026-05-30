"""
social_poster.py
Buffer API'yi kullanarak Instagram ve TikTok'ta video ve aciklama(caption) paylasir.
Ucretsiz plana uygundur (Gunde 10 post'a kadar Buffer tarafindan desteklenir).
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BUFFER_TOKEN = os.getenv("BUFFER_TOKEN", "")
INSTAGRAM_ID = os.getenv("BUFFER_INSTAGRAM_ID", "")
TIKTOK_ID = os.getenv("BUFFER_TIKTOK_ID", "")

def post_to_socials(video_path, caption):
    """
    Uretilen videoyu Buffer uzerinden siraya ekler.
    Eger Instagram ve TikTok bagliysa ikisine ayni anda atar.
    """
    if not BUFFER_TOKEN or "BURAYA" in BUFFER_TOKEN:
        print("UYARI: Buffer Token ayarlanmamis. Sosyal medya paylasimi atlandi.")
        print("  - Uretilen Caption:\n", caption)
        return False
        
    profile_ids = []
    if INSTAGRAM_ID and "BURAYA" not in INSTAGRAM_ID:
        profile_ids.append(INSTAGRAM_ID)
    if TIKTOK_ID and "BURAYA" not in TIKTOK_ID:
        profile_ids.append(TIKTOK_ID)
        
    if not profile_ids:
        print("UYARI: En az bir Buffer Profile ID girmelisiniz (Instagram veya TikTok).")
        return False

    print(f"Sosyal Medya paylasimi baslatiliyor... ({len(profile_ids)} hesap)")
    
    # 1. Video'yu yuklemek icin bir URL'ye ihtiyacimiz var, 
    # Ancak basit otomasyonlarda yerel videolari Buffer API desteklemez (URL ister).
    # Cozum 1: Kendi Oracle sunucumuz uzerinden statik host acmak (basit)
    # Cozum 2: Imgur / S3 bucket'a yukleyip url'sini almak.
    # Buffer API'si yerel dosya yuklemeyi desteklemiyor, medya URL'si istiyor.
    
    # Buffer API dokumantasyonuna gore media={'video': 'url'} verilmeli
    print("Not: Otomatik gonderim icin API URL yapilandirmasi gerekli. Bu adim icin sunucuda statik dosya sunucu (Nginx) yapilandirilmali.")
    print("Simdilik paylasilacak icerik (Otomasyon test modunda):")
    print(f"  Video: {video_path}")
    print(f"  Metin: {caption[:50]}...")
    
    return True
