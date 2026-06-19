import os
import csv
import json
import random
import requests
import argparse
from datetime import datetime
from PIL import Image
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from rembg import remove
from content import video_generator
from content.prompt_generator import generate_social_caption
from etsy import fetcher as etsy_fetcher


os.makedirs("bulk_images", exist_ok=True)

def get_all_products():
    return etsy_fetcher.get_all_products()

def extract_raw_design_url(product):
    # Printify ürünündeki ilk baskı alanının görselini bul
    for print_area in product.get("print_areas", []):
        for placeholder in print_area.get("placeholders", []):
            for img in placeholder.get("images", []):
                if img.get("src"):
                    return img["src"]
    return None

def generate_metalhead_model():
    prompts = [
        "a badass heavy metal musician with long black hair, tattoos, wearing a PLAIN BLACK T-SHIRT (no logos, no graphics, completely blank), performing on a dark stage with red laser lights, epic photorealistic concert photography",
        "a female goth rocker with dramatic makeup and piercings, wearing a PLAIN BLACK T-SHIRT (completely blank), in a smoky underground club, neon purple lighting, photorealistic 8k",
        "a heavy metal fan in a mosh pit, wearing a PLAIN BLACK T-SHIRT (no logos), surrounded by fog and strobe lights, dark and aggressive aesthetic, cinematic photography",
        "a death metal guitarist looking intensely at the camera, wearing a PLAIN BLACK T-SHIRT (blank), against a brick wall with graffiti, moody and dark lighting, 4k"
    ]
    prompt = random.choice(prompts)
    encoded_prompt = requests.utils.quote(prompt)
    # nologo=true ile tamamen boş tişört garantiye alınır
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux-realism&nologo=true"
    
    # Retry logic for Pollinations API (often hangs or times out)
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=45)
            if resp.status_code == 200:
                return resp.content
            print(f"      Attempt {attempt+1} failed with status {resp.status_code}. Retrying...")
        except Exception as e:
            print(f"      Attempt {attempt+1} timed out or failed: {e}")
        time.sleep(2)
        
    return None

def composite_design_on_model(model_bytes, design_bytes, output_filename):
    try:
        from io import BytesIO
        import numpy as np
        model_img = Image.open(BytesIO(model_bytes)).convert("RGBA")
        design_img = Image.open(BytesIO(design_bytes)).convert("RGBA")
        
        # Tişörtün göğüs bölgesine oturtmak için boyutu ayarla
        target_width = 320
        ratio = target_width / design_img.width
        target_height = int(design_img.height * ratio)
        design_resized = design_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        pos_x = (1024 - target_width) // 2
        pos_y = (1024 - target_height) // 2 - 30 # Göğüs hizasına çek
        
        # 1. Manken resminden tişört alanının dokusunu (gölgeler/kırışıklıklar) al
        chest_region = model_img.crop((pos_x, pos_y, pos_x + target_width, pos_y + target_height))
        # Grayscale yap (parlaklık haritası)
        gray_region = chest_region.convert("L")
        
        # 2. Parlaklık haritasını normalize et
        # Çok derin gölgeleri ve aşırı parlamaları engellemek için sınırlayalım
        gray_arr = np.array(gray_region, dtype=np.float32)
        mean_val = np.mean(gray_arr)
        if mean_val == 0:
            mean_val = 1.0
            
        # Doku çarpanı: (Piksel Değeri / Ortalama Parlaklık)
        mul_map = gray_arr / mean_val
        mul_map = np.clip(mul_map, 0.45, 1.15) # Tasarımın gölgede kararmasını ve ışıkta parlamasını sağlar
        
        # 3. Tasarımın piksellerini bu harita ile çarp
        design_arr = np.array(design_resized, dtype=np.float32)
        for c in range(3): # Sadece RGB kanallarını çarp, Alpha kanalı sabit
            design_arr[..., c] *= mul_map
            
        design_arr = np.clip(design_arr, 0, 255).astype(np.uint8)
        design_blended = Image.fromarray(design_arr, "RGBA")
        
        # 4. Harmanlanmış tasarımı ana resmin üzerine yapıştır
        design_layer = Image.new("RGBA", model_img.size, (0, 0, 0, 0))
        design_layer.paste(design_blended, (pos_x, pos_y), mask=design_resized)
        
        final_img = Image.alpha_composite(model_img, design_layer)
        final_img.convert("RGB").save(f"bulk_images/{output_filename}", quality=95)
        return True
    except Exception as e:
        print(f"Error compositing image: {e}")
        return False


def main(batch_limit=1, force_id=None):
    print(f"Starting Bulk Content Generator (Limit: {batch_limit})...")
    products = get_all_products()
    if force_id:
        products = [p for p in products if str(p.get("id")) == str(force_id)]
    if not products:
        print("No products found.")
        return
        
    posted_products = {}
    if os.path.exists("assets/posted_products.json"):
        with open("assets/posted_products.json", "r", encoding="utf-8") as f:
            try:
                posted_products = json.load(f)
            except:
                pass
                
    # processed_ids from CSV
    processed_ids = set()
    csv_file = "bulk_schedule.csv"
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if len(row) > 1:
                    pid = row[2].replace('post_', '').replace('.jpg', '')
                    processed_ids.add(pid)
                    
    print(f"-> Found {len(processed_ids)} products in CSV and {len(posted_products)} in JSON.")
    
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["IG_TikTok_Text", "Pinterest_Text", "Image_File", "Video_File", "Product_URL", "Status"])
            
        generated_count = 0
        for idx, product in enumerate(products):
            print(f"\n[{idx+1}/{len(products)}] Processing: {product.get('title')}")
            
            product_id = product["id"]
            
            is_published_or_skipped = False
            if str(product_id) in posted_products:
                status = posted_products[str(product_id)].get("status")
                if status in ["PUBLISHED", "SKIPPED"]:
                    is_published_or_skipped = True

            if (str(product_id) in processed_ids or is_published_or_skipped) and str(product_id) != str(force_id):
                print("-> Already processed, skipping.")
                continue
                
            # E-ticaret panelinden silinmiş ama API'de kalmış ürünleri kara listeye al
            EXCLUDED_PRODUCT_IDS = [
                "693f177ffef9882cd50173b1"  # Silinen Rammstein Hoodie
            ]
            if product_id in EXCLUDED_PRODUCT_IDS:
                print("-> Product is blacklisted (deleted on store), skipping.")
                continue
                
            # Etsy API'den gelen resim modelini al
            images = product.get("images", [])
            mockup_url = None
            if images:
                mockup_url = images[0].get("src")
            
            clean_title = product.get("title", "").replace(".", "")
            if "hoodie" not in clean_title.lower() and "t-shirt" not in clean_title.lower() and "tshirt" not in clean_title.lower() and "sweatshirt" not in clean_title.lower():
                print(f"-> Skipping non-apparel product: {clean_title}")
                continue
                
            if not mockup_url:
                print("-> No product mockup image found, skipping.")
                continue
                
            print("-> Downloading Printify product mockup...")
            mockup_resp = requests.get(mockup_url)
            if mockup_resp.status_code != 200:
                print("-> Failed to download mockup.")
                continue
                
            import re
            safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', clean_title.strip())
            safe_title = re.sub(r'_+', '_', safe_title).strip('_')
            if not safe_title:
                safe_title = f"product_{product['id']}"
                
            product_dir = f"media/{safe_title}"
            os.makedirs(product_dir, exist_ok=True)
            
            filename = "image.png"
            image_path = f"{product_dir}/{filename}"
            
            # Orijinal Printify mockup resmini doğrudan kaydet ve arka planı sil!
            print(f"-> Removing background from mockup and saving to {image_path}...")
            try:
                transparent_img = remove(mockup_resp.content)
                with open(image_path, "wb") as f_img:
                    f_img.write(transparent_img)
                print("-> Printify transparent mockup saved successfully.")
            except Exception as e:
                print(f"-> Background removal failed: {e}. Saving original.")
                filename = "image.jpg"
                image_path = f"{product_dir}/{filename}"
                with open(image_path, "wb") as f_img:
                    f_img.write(mockup_resp.content)
                
            print("-> Generating caption...")
            clean_title = product.get("title", "").replace(".", "")
            
            # Ürünün tipini tahmin et
            product_type = "tshirt"
            if "hoodie" in clean_title.lower():
                product_type = "hoodie"
            elif "sweatshirt" in clean_title.lower():
                product_type = "sweatshirt"
                
            social_data = generate_social_caption(clean_title)
            hook_text = social_data.get("hook", "")
            social_data["product_id"] = product["id"]
            
            print(f"-> Generating TikTok/Reels video in {product_dir}...")
            video_filename = "video.mp4"
            video_path = f"{product_dir}/{video_filename}"
            video_generator.generate_tiktok_video(image_path, video_path, hook_text=hook_text, product_type=product_type)
            
            product_url = product.get("url", "https://www.etsy.com/shop/Deathlipse")
            
            # JSON'ı encode edip CSV'ye yazalım, telegram_bot.py oradan okusun
            social_json_str = json.dumps(social_data)
            writer.writerow([social_json_str, social_data.get("pinterest", ""), image_path, video_path, product_url, "PENDING"])
            print("-> Successfully added to bulk_schedule.csv!")
            
            # Kalici listeye ekle
            posted_products[product['id']] = {
                "title": product['title'],
                "posted_at": datetime.now().isoformat(),
                "status": "PENDING"
            }
            with open("assets/posted_products.json", "w", encoding="utf-8") as f:
                json.dump(posted_products, f, indent=4)
            
            generated_count += 1
            if generated_count >= batch_limit:
                print(f"\n[STOP] Batch limit of {batch_limit} videos generated successfully.")
                break
                
            time.sleep(2)
            
    print("\nDONE! All posts generated in 'bulk_images/' & 'reels_output/' and 'bulk_schedule.csv' is ready for upload!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate bulk content for Deathlipse Bot")
    parser.add_argument("--batch", type=int, default=1, help="Number of products to generate (default: 1)")
    parser.add_argument("--force-id", type=str, default=None, help="Force processing a specific product ID")
    args = parser.parse_args()
    
    # Check if limit is specified in env, args override env
    env_limit = os.getenv("BATCH_LIMIT")
    batch_limit = args.batch
    if env_limit and batch_limit == 1:
        batch_limit = int(env_limit)
        
    main(batch_limit, force_id=args.force_id)
