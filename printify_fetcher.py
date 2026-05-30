"""
printify_fetcher.py
Printify API'den tum urun gorsellerini otomatik indirir.
"""
import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PRINTIFY_TOKEN = os.getenv("PRINTIFY_TOKEN")
SHOP_ID = os.getenv("PRINTIFY_SHOP_ID", "14366005")
HEADERS = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
BASE_URL = "https://api.printify.com/v1"


def get_all_products():
    """Magazadaki tum aktif urunleri cek"""
    all_products = []
    page = 1
    
    while True:
        url = f"{BASE_URL}/shops/{SHOP_ID}/products.json?limit=50&page={page}"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        
        if resp.status_code != 200:
            print(f"HATA: {resp.status_code} - {resp.text}")
            break
        
        data = resp.json()
        products = data.get("data", [])
        
        if not products:
            break
        
        all_products.extend(products)
        
        # Son sayfa kontrolu
        if len(products) < 50:
            break
        
        page += 1
    
    print(f"Toplam {len(all_products)} urun bulundu.")
    return all_products


def download_product_images(product):
    """
    Bir urunun on cephe (front) mockup gorsellerini indir.
    Her urun icin /assets/images/{product_id}/ klasorune kaydet.
    """
    product_id = product["id"]
    title = product["title"]
    images = product.get("images", [])
    
    save_dir = Path(f"assets/images/{product_id}")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Oncelik sirasi: front > main > diger
    # Tüm görselleri indir (Limit yok, ön/arka kısıtlaması yok)
    selected = []
    
    for img in images:
        is_default = img.get("is_default", False)
        if is_default:
            selected.insert(0, img)
        else:
            selected.append(img)

    
    saved_paths = []
    for i, img in enumerate(selected):
        src = img.get("src", "")
        img_path = save_dir / f"img_{i}.jpg"
        
        # Zaten varsa atla
        if img_path.exists() and img_path.stat().st_size > 10000:
            saved_paths.append(str(img_path))
            continue
        
        try:
            resp = requests.get(src, timeout=30)
            if resp.status_code == 200:
                img_path.write_bytes(resp.content)
                saved_paths.append(str(img_path))
                print(f"  Indirildi: {img_path.name}")
        except Exception as e:
            print(f"  Gorsel indirilemedi: {e}")
    
    # Fiyat bilgisini al
    price = 0
    variants = product.get("variants", [])
    if variants:
        price = variants[0].get("price", 0) / 100
    
    return {
        "id": product_id,
        "title": title,
        "images": saved_paths,
        "price": price,
        "product_type": detect_product_type(title)
    }


def detect_product_type(title):
    """Urun basligindan tipi tespit et"""
    title_lower = title.lower()
    if "hoodie" in title_lower:
        return "hoodie"
    elif "sweatshirt" in title_lower or "crewneck" in title_lower:
        return "sweatshirt"
    elif "tank" in title_lower:
        return "tank top"
    elif "tote" in title_lower or "bag" in title_lower:
        return "tote bag"
    elif "poster" in title_lower:
        return "poster"
    else:
        return "t-shirt"


def fetch_all_and_save():
    """
    Tum urunleri cek, gorsellerini indir ve JSON cache olustur.
    Bu fonksiyon her gun bir kez calistirilir.
    """
    print("\nPrintify'dan urunler cekiliyor...")
    products = get_all_products()
    
    result = []
    for p in products:
        print(f"\nIslem: {p['title'][:60]}")
        product_data = download_product_images(p)
        
        if product_data["images"]:  # Sadece gorseli olanlar
            result.append(product_data)
    
    # Cache dosyasina kaydet
    cache_path = Path("assets/products.json")
    cache_path.parent.mkdir(exist_ok=True)
    cache_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    print(f"\n{len(result)} urun basariyla islendi ve cache'e kaydedildi.")
    return result


if __name__ == "__main__":
    products = fetch_all_and_save()
    print("\nOrnek urunler:")
    for p in products[:3]:
        print(f"  - {p['title'][:50]} | {len(p['images'])} gorsel | ${p['price']}")
