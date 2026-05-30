import os
import json
import requests
from dotenv import load_dotenv
from llama4_maverick_engine import analyze_product_with_llama4

# --- CONFIGURATION ---
load_dotenv()
PRINTIFY_TOKEN = os.getenv("PRINTIFY_TOKEN")
SHOP_ID = os.getenv("PRINTIFY_SHOP_ID", "14366005")

HEADERS = {
    "Authorization": f"Bearer {PRINTIFY_TOKEN}",
    "Content-Type": "application/json"
}

def extract_raw_design_url(product):
    """Printify ürünündeki ilk baskı alanının görsel URL'sini çıkarır"""
    for print_area in product.get("print_areas", []):
        for placeholder in print_area.get("placeholders", []):
            for img in placeholder.get("images", []):
                if img.get("src"):
                    return img["src"]
    return None

def update_product(product_id, seo_data):
    url = f"https://api.printify.com/v1/shops/{SHOP_ID}/products/{product_id}.json"
    
    # Printify beklentisine göre payload hazırlama
    payload = {
        "title": seo_data["title"],
        "description": seo_data["description"],
        "tags": seo_data["tags"]
    }
    
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"Product {product_id} updated successfully on Printify.")
        return True
    else:
        print(f"Error updating product: {response.text}")
        return False

def publish_to_etsy(product_id):
    url = f"https://api.printify.com/v1/shops/{SHOP_ID}/products/{product_id}/publish.json"
    
    # Etsy'ye sadece title, description ve tags değişikliklerini gönder
    payload = {
        "title": True,
        "description": True,
        "tags": True,
        "images": False,
        "variants": False
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"Product {product_id} successfully published/pushed to Etsy!")
    else:
        print(f"Error publishing to Etsy: {response.text}")

def get_all_products():
    url = f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error fetching products: {response.text}")
        return []

def main():
    print("--- DEATHLIPSE ETSY SEO AUTOMATOR (V2 - Llama-4 Maverick Multimodal) ---")
    
    print("1. Fetching all products from Printify...")
    products = get_all_products()
    
    if not products:
        print("No products found.")
        return
        
    print(f"Found {len(products)} products. Starting Multimodal SEO optimization...\n")
    
    import time
    for product in products:
        product_id = product["id"]
        current_title = product.get("title", "")
        print("="*50)
        print(f"Processing: {current_title} ({product_id})")
        
        image_url = extract_raw_design_url(product)
        if not image_url:
            print("-> No image found. Llama-4 will rely on text only.")
        
        print("-> Generating SEO Content with Llama-4 Maverick (Multimodal)...")
        seo_data = analyze_product_with_llama4(current_title, image_url)
        
        if seo_data:
            print(f"-> TITLE: {seo_data.get('title')}")
            print(f"-> TAGS: {', '.join(seo_data.get('tags', []))}")
            
            # Güncelleme işlemini yap
            if update_product(product_id, seo_data):
               print("-> Publishing to Etsy...")
               publish_to_etsy(product_id)
               time.sleep(8) # Printify rate limit önlemi ("Too Many Attempts" hatasını önlemek için)
        
        print("="*50 + "\n")

if __name__ == "__main__":
    main()
