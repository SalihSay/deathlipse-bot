"""
main.py
Deathlipse Tam Otomatik Video Pazarlama Botu
Hicbir butce gerektirmeyen %100 Ucretsiz Yapay Zeka Video Otomasyonu
"""
import os
import time
import schedule
import json
import random
from pathlib import Path
from printify_fetcher import get_all_products, download_product_images, detect_product_type
from prompt_generator import generate_video_prompt, generate_caption
from video_generator import generate_video_free
from social_poster import post_to_socials

def job_create_daily_post():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] GUNLUK OTOMASYON BASLIYOR...")
    
    # 1. Printify'dan rastgele 1 urun sec (tumunu indirmek yerine cache kullanalim)
    cache_file = Path("assets/products.json")
    if not cache_file.exists():
        print("Urun cache bulunamadi. Printify'dan guncelleniyor...")
        # Tumunu guncelle (Bunu yapinca cache olusur)
        os.system("python printify_fetcher.py")
        
    products = json.loads(cache_file.read_text(encoding="utf-8"))
    products_with_images = [p for p in products if p.get("images")]
    
    if not products_with_images:
        print("HATA: Hic urun gorseli yok.")
        return
        
    # Rastgele bir urun sec (Her gun farkli post)
    chosen_product = random.choice(products_with_images)
    print(f"Secilen Urun: {chosen_product['title']}")
    
    # 2. AI Prompt ve Caption Uretimi (Groq)
    print("AI promptlar uretiliyor...")
    ptype = chosen_product.get("product_type", "t-shirt")
    price = chosen_product.get("price", 29.99)
    image_path = chosen_product["images"][0]
    
    video_prompt = generate_video_prompt(chosen_product["title"], ptype)
    caption = generate_caption(chosen_product["title"], ptype, price)
    
    # 3. AI Video Uretimi (Hugging Face - Ucretsiz Wan2.1)
    print("Hugging Face'e video uretim emri gonderiliyor...")
    video_path = generate_video_free(image_path, video_prompt, chosen_product["id"])
    
    if not video_path:
        print("Video uretilemedi, iptal ediliyor.")
        return
        
    # 4. Sosyal Medyada Paylasim Onayi (Manuel Kontrol)
    print("\n" + "="*40)
    print("VİDEO HAZIR! Lütfen videoyu kontrol edin:")
    print(f"Klasör Yolu: C:\\Users\\ASUS\\OneDrive\\Desktop\\deathlipse-bot\\{video_path}")
    print(f"Hazırlanan Metin:\n{caption}")
    print("="*40)
    
    onay = input("Bu videoyu sosyal medyada paylaşmak istiyor musunuz? (E/H): ")
    
    if onay.lower() == 'e':
        print("Sosyal medyada paylasiliyor...")
        post_to_socials(video_path, caption)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] OTOMASYON BASARIYLA TAMAMLANDI!\n")
    else:
        print("Paylaşım iptal edildi. Otomasyon durdu.")

def run_scheduler():
    print("========================================")
    print("DEATHLIPSE BOT BASLATILDI")
    print("========================================")
    print("- %100 Ucretsiz Yapi (Groq + HF Spaces)")
    print("- Her gun saat 19:00'da (TR Saati) paylasim yapacak sekilde ayarlandi.")
    
    # Gunde 1 kez calistir (Kendi saat dilimine gore ayarla)
    schedule.every().day.at("19:00").do(job_create_daily_post)
    
    # Test amacli hemen bir kere calistir:
    job_create_daily_post()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
