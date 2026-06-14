import os
import requests
import json
from pathlib import Path
from core.config import ETSY_API_KEY, ETSY_SHARED_SECRET, ETSY_SHOP_ID, ETSY_ACCESS_TOKEN


def get_headers(use_oauth=False):
    headers = {
        "x-api-key": f"{ETSY_API_KEY}:{ETSY_SHARED_SECRET}",
        "Content-Type": "application/json"
    }
    if use_oauth and ETSY_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ETSY_ACCESS_TOKEN}"
    return headers

def get_all_products():
    """Mağazadaki tüm aktif ürünleri (Etsy) çek"""
    all_products = []
    limit = 100
    offset = 0
    
    while True:
        url = f"https://openapi.etsy.com/v3/application/shops/{ETSY_SHOP_ID}/listings/active?includes=Images&limit={limit}&offset={offset}"
        resp = requests.get(url, headers=get_headers(), timeout=30)
        
        if resp.status_code != 200:
            print(f"ETSY GET HATA: {resp.status_code} - {resp.text}")
            break
            
        data = resp.json()
        results = data.get("results", [])
        
        if not results:
            break
            
        # Modeli uygulamanın geneline uygun hale getir (Printify verisi gibi standartlastir)
        for item in results:
            product = {
                "id": str(item.get("listing_id")),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "tags": item.get("tags", []),
                "price": item.get("price", {}).get("amount", 0) / item.get("price", {}).get("divisor", 1), # Fiyat hesabı
                "url": item.get("url", ""),
                "images": []
            }
            # Resimleri ekle (Her urun icin ayri istek)
            try:
                img_url = f"https://openapi.etsy.com/v3/application/listings/{item.get('listing_id')}/images"
                img_resp = requests.get(img_url, headers=get_headers(), timeout=10)
                if img_resp.status_code == 200:
                    images_data = img_resp.json().get("results", [])
                    for img in images_data:
                        product["images"].append({
                            "src": img.get("url_fullxfull")
                        })
            except Exception as e:
                print(f"Resim cekme hatasi {item.get('listing_id')}: {e}")
            
            all_products.append(product)
            
        if len(results) < limit:
            break
        offset += limit
            
        offset += limit
        
    print(f"Toplam {len(all_products)} ürün Etsy'den başarıyla çekildi.")
    return all_products

def download_product_images(product):
    """
    Bir ürünün ana görselini (images[0].url_fullxfull) indirir.
    /assets/images/{product_id}/ klasörüne kaydeder.
    """
    product_id = product["id"]
    images = product.get("images", [])
    
    save_dir = Path(f"assets/images/{product_id}")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    if not images:
        print(f"Ürün {product_id} için görsel bulunamadı.")
        return []
        
    # Sadece ilk ana fotoğrafı alalım
    main_img = images[0]
    src = main_img.get("src", "")
    if not src:
        return []
        
    img_path = save_dir / "img_1.jpg"
    try:
        resp = requests.get(src, timeout=30)
        if resp.status_code == 200:
            img_path.write_bytes(resp.content)
            return [{"path": img_path}]
    except Exception as e:
        print(f"Görsel indirme hatası {product_id}: {e}")
        
    return []

def update_listing(listing_id, title=None, description=None, tags=None):
    """
    Etsy ürününün başlığını, açıklamasını ve etiketlerini günceller.
    NOT: Bu işlem için ETSY_ACCESS_TOKEN (OAuth) gerekir!
    """
    url = f"https://openapi.etsy.com/v3/application/shops/{ETSY_SHOP_ID}/listings/{listing_id}"
    
    payload = {}
    if title:
        payload["title"] = title[:140] # Etsy limit
    if description:
        payload["description"] = description
    if tags:
        payload["tags"] = tags[:13] # Etsy tags limit
        
    if not payload:
        return False
        
    try:
        resp = requests.put(url, json=payload, headers=get_headers(use_oauth=True), timeout=30)
        if resp.status_code in [200, 201]:
            print(f"Listing {listing_id} başarıyla güncellendi.")
            return True
        else:
            print(f"Listing güncellenemedi: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"Etsy PUT Exception: {e}")
        return False
