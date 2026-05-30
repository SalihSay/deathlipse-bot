import os
import csv
import json
import random
import requests
from PIL import Image
from dotenv import load_dotenv
import time

load_dotenv()
PRINTIFY_TOKEN = os.getenv("PRINTIFY_TOKEN")
SHOP_ID = os.getenv("PRINTIFY_SHOP_ID", "14366005")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {PRINTIFY_TOKEN}",
    "Content-Type": "application/json"
}

os.makedirs("bulk_images", exist_ok=True)

def get_all_products():
    url = f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

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

def generate_social_caption(product_title):
    prompt = f"""
    You are the elite social media manager for DEATHLIPSE, an underground heavy metal apparel brand.
    Write social media copy for this product: {product_title}
    
    Rules for IG_TikTok:
    1. Max 2 short, punchy sentences. Dark, aggressive, edgy tone.
    2. Inject scarcity/urgency (e.g., "Limited stock", "Underground exclusive").
    3. Direct Call to Action: Tell them exactly what to do (e.g., "Wear the darkness. ↓ Link in bio to shop ↓").
    4. Exactly 10 targeted heavy metal/goth hashtags.
    
    Rules for Pinterest:
    1. Write a 3-4 sentence SEO-optimized description targeting US buyers searching for heavy metal fashion.
    2. Focus on keywords like "alternative clothing", "goth aesthetic", "vintage metal shirt".
    3. End with "Shop the collection now."
    
    Return EXACTLY a raw JSON object and nothing else. No markdown formatting.
    {{
      "ig_tiktok": "Caption here... #hashtags",
      "pinterest": "SEO description here..."
    }}
    """
    
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "response_format": {"type": "json_object"}
            },
            timeout=30,
        )
        if resp.status_code == 200:
            result = json.loads(resp.json()["choices"][0]["message"]["content"])
            return result.get("ig_tiktok", ""), result.get("pinterest", "")
    except Exception as e:
        print(f"Error generating caption: {e}")
        
    fallback_ig = f"Unleash the darkness. Limited drop of the {product_title}. ↓ Link in bio to shop ↓\n\n#heavymetal #metalhead #deathmetal #blackmetal #goth #metalmerch #altfashion #darkaesthetic #metalclothing #metalstyle"
    fallback_pin = f"Discover the {product_title} from Deathlipse. Perfect for your dark aesthetic and heavy metal wardrobe. High-quality alternative clothing and goth fashion. Shop the collection now."
    return fallback_ig, fallback_pin

def main():
    print("--- BULK SOCIAL MEDIA GENERATOR (BUFFER/METRICOOL) ---")
    products = get_all_products()
    if not products:
        print("No products found.")
        return
        
    print(f"Found {len(products)} products.")
    
    processed_ids = set()
    csv_file = "bulk_schedule.csv"
    file_exists = os.path.isfile(csv_file)
    
    if file_exists:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 1 and row[1].startswith('post_'):
                    # filename is like post_6706591e158d8c4d550f058c.jpg
                    pid = row[1].replace('post_', '').replace('.jpg', '')
                    processed_ids.add(pid)
                    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Buffer CSV formati (genellikle): Text, Media URL / Path
        if not file_exists:
            writer.writerow(["IG_TikTok_Text", "Pinterest_Text", "Image_File", "Video_File", "Product_URL", "Status"])
            
        import video_generator
        generated_count = 0
        for idx, product in enumerate(products):
            print(f"\n[{idx+1}/{len(products)}] Processing: {product.get('title')}")
            
            product_id = product["id"]
            if product_id in processed_ids:
                print("-> Already processed, skipping.")
                continue
                
            # E-ticaret panelinden silinmiş ama API'de kalmış ürünleri kara listeye al
            EXCLUDED_PRODUCT_IDS = [
                "693f177ffef9882cd50173b1"  # Silinen Rammstein Hoodie
            ]
            if product_id in EXCLUDED_PRODUCT_IDS:
                print("-> Product is blacklisted (deleted on store), skipping.")
                continue
                
            # GÜNCELLİK KONTROLLERİ:
            # 1. Ürün Printify üzerinde gizlenmiş veya yayından kaldırılmış mı?
            if not product.get("visible", True):
                print("-> Product is not visible/published, skipping.")
                continue
                
            # 2. Ürün aktif bir mağazaya (Etsy vb.) bağlı mı?
            if not product.get("external"):
                print("-> Product is a draft (not connected to Etsy), skipping.")
                continue
            
            # Printify'daki default mockup görselini bul
            images = product.get("images", [])
            mockup_url = None
            for img in images:
                if img.get("is_default", False):
                    mockup_url = img.get("src")
                    break
            
            if not mockup_url and images:
                mockup_url = images[0].get("src")
                
            if not mockup_url:
                print("-> No product mockup image found, skipping.")
                continue
                
            print("-> Downloading Printify product mockup...")
            mockup_resp = requests.get(mockup_url)
            if mockup_resp.status_code != 200:
                print("-> Failed to download mockup.")
                continue
                
            filename = f"post_{product['id']}.jpg"
            # Orijinal Printify mockup resmini doğrudan kaydet
            with open(f"bulk_images/{filename}", "wb") as f_img:
                f_img.write(mockup_resp.content)
            print("-> Printify mockup saved successfully.")
                
            print("-> Generating TikTok/Reels video...")
            video_filename = f"reel_{product['id']}.mp4"
            video_path = f"reels_output/{video_filename}"
            video_generator.generate_tiktok_video(f"bulk_images/{filename}", video_path)
                
            print("-> Generating caption...")
            clean_title = product.get("title", "").replace(".", "")
            ig_caption, pin_caption = generate_social_caption(clean_title)
            
            product_url = f"https://www.etsy.com/shop/Deathlipse"
            
            ig_text = f"{ig_caption}\n\n{product_url}"
            pin_text = f"{pin_caption}\n\n{product_url}"
            writer.writerow([ig_text, pin_text, filename, video_filename, product_url, "PENDING"])
            print("-> Successfully added to bulk_schedule.csv!")
            
            generated_count += 1
            if generated_count >= 3:
                print("\n[STOP] Test mode: 3 videos generated successfully. Limit reached.")
                break
                
            time.sleep(2)
            
    print("\nDONE! All posts generated in 'bulk_images/' & 'reels_output/' and 'bulk_schedule.csv' is ready for upload!")

if __name__ == "__main__":
    main()
