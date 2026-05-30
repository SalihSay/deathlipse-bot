"""
test_poster_nvidia.py
NVIDIA NIM (FLUX.1-dev) + AI Compositing Sistemi
Gerçek ürün görselinin arka planını temizler ve yapay zekanın ürettiği
fotogerçekçi stüdyo ortamına yerleştirir.
"""
import os
import io
import json
import random
import base64
import requests
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import rembg

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# ==========================================
# KATEGORI BAZLI ARKA PLAN PROMPT SABLONLARI
# Ürünün BENDEN BAĞIMSIZ "oturtulacağı" sahneyi tasvir eder.
# Ürünün kendisinden (Tişört vb.) hiç BAhSETMEYIZ, sadece mekanı/boşluğu betimleriz.
# ==========================================
# ==========================================
# KATEGORI BAZLI ARKA PLAN PROMPT SABLONLARI
# ==========================================
BACKGROUND_PROMPTS = {
    "t-shirt": [
        "A highly detailed heavy metal concert stage. Massive black amplifier stacks in the background, vibrant piercing red laser lights cutting through thick atmospheric fog. A roaring crowd in silhouette in the distance. Cinematic lighting, epic rock and roll atmosphere, 8k resolution, photorealistic",
        "An atmospheric dark Gothic alleyway at night. Wet cobblestones reflecting bright red and purple neon lights from a vintage bar sign. Heavy metal grunge aesthetic, thick smoke, moody dramatic shadows, intricate details, 8k resolution, highly detailed photography"
    ],
    "hoodie": [
        "Inside an abandoned industrial warehouse with dark rusty concrete walls. Glowing amber fire embers floating in the air. A vintage electric guitar leaning against a heavy metal crate. Atmospheric smoke, cinematic lighting, dramatic mood, highly detailed 8k photography",
    ],
    "default": [
        "A highly detailed heavy metal concert stage. Massive black amplifier stacks in the background, vibrant piercing red laser lights cutting through thick atmospheric fog. Epic rock and roll atmosphere, 8k resolution, photorealistic",
    ]
}

def detect_category(title):
    title_lower = title.lower()
    if "hoodie" in title_lower:
        return "hoodie"
    elif "sweatshirt" in title_lower or "crewneck" in title_lower:
        return "hoodie"
    elif "t-shirt" in title_lower or "tee" in title_lower or "shirt" in title_lower:
        return "t-shirt"
    return "default"

def generate_ai_background(category):
    if not NVIDIA_API_KEY:
        return None

    templates = BACKGROUND_PROMPTS.get(category, BACKGROUND_PROMPTS["default"])
    prompt = random.choice(templates)
    
    print(f"  AI Arka Plan Prompt: {prompt[:100]}...")
    url = 'https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev'
    headers = {
        'Authorization': f'Bearer {NVIDIA_API_KEY}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'prompt': prompt,
        'width': 1024,
        'height': 1024,
        'cfg_scale': 5,
        'steps': 30,
        'seed': random.randint(0, 10000),
        'samples': 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            img_data = base64.b64decode(data['artifacts'][0]['base64'])
            return Image.open(io.BytesIO(img_data)).convert("RGBA")
    except Exception as e:
        print(f"  HATA: {e}")
        return None

def process_product_image(image_path):
    print("  Urun gorselinin arka plani siliniyor (rembg)...")
    try:
        with open(image_path, "rb") as i:
            input_data = i.read()
            # rembg kullanarak arka planı sil (manken kalacak, arka plan gidecek)
            output_data = rembg.remove(input_data)
            img = Image.open(io.BytesIO(output_data)).convert("RGBA")
            
            # Alt kısımdaki sert kesikleri yumuşatmak için hafif bir gradient/feather ekleyebiliriz ama 
            # en alta hizalayacağımız için sorun olmayacaktır.
            return img
    except Exception as e:
        print(f"  HATA: {e}")
        return None

from PIL import ImageFilter

def create_drop_shadow(image, offset=(15, 15), blur_radius=10, opacity=150):
    """Ürün görseli için gerçekçi bir gölge (drop shadow) oluşturur"""
    mask = image.split()[3]
    shadow = Image.new("RGBA", image.size, color=(0, 0, 0, 0))
    shadow.paste((0, 0, 0, opacity), (0, 0), mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    
    total_width = image.width + abs(offset[0]) + blur_radius * 2
    total_height = image.height + abs(offset[1]) + blur_radius * 2
    
    canvas = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
    
    shadow_x = blur_radius + max(0, offset[0])
    shadow_y = blur_radius + max(0, offset[1])
    img_x = blur_radius + max(0, -offset[0])
    img_y = blur_radius + max(0, -offset[1])
    
    canvas.alpha_composite(shadow, dest=(shadow_x, shadow_y))
    canvas.alpha_composite(image, dest=(img_x, img_y))
    
    return canvas

def create_composite_poster(product):
    title = product.get("title", "")
    category = detect_category(title)
    
    images = product.get("images", [])
    if not images:
        return False
        
    if len(images) > 6:
        local_img_path = images[6] # Rammstein sırt tasarımı olan manken
    else:
        local_img_path = images[-1]
        
    if not os.path.exists(local_img_path):
        return False
        
    product_img = process_product_image(local_img_path)
    if not product_img:
        return False
        
    bg_img = generate_ai_background(category)
    if not bg_img:
        return False
        
    print("  Gorseller birlestiriliyor (Portre Modu Hizalamasi)...")
    
    bg_w, bg_h = bg_img.size
    
    # Mankenin boyunu arka planın %90'ı yapalım (daha büyük ve heybetli dursun)
    target_height = int(bg_h * 0.90)
    aspect_ratio = product_img.width / product_img.height
    target_width = int(target_height * aspect_ratio)
    
    product_img = product_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Çok hafif bir genel gölge (Ambient Occlusion) ekleyerek yapıştırılmış hissini kırma
    product_with_shadow = create_drop_shadow(product_img, offset=(0, 0), blur_radius=25, opacity=120)
    
    # Gölgeyi de hesaplayarak ortalama ve en alta hizalama
    offset_x = (bg_w - product_with_shadow.width) // 2
    offset_y = bg_h - product_with_shadow.height # Tam alta yapıştır
    
    bg_img.alpha_composite(product_with_shadow, dest=(offset_x, offset_y))
    
    output_path = "test_poster_composite_result.png"
    final_img = bg_img.convert("RGB")
    final_img.save(output_path)
    print(f"  BASARILI! Yeni poster kaydedildi: {output_path}")
    return output_path


if __name__ == "__main__":
    cache_path = Path("assets/products.json")
    if cache_path.exists():
        products = json.loads(cache_path.read_text(encoding="utf-8"))
        
        # Kullanıcının tasarımını görebilmesi için ÖZELLİKLE tasarımlı bir ürün seçelim
        # "Unisex Heavy Blend" isimli ürünlerde sadece boş tişört resmi olabiliyor!
        target_product = None
        for p in products:
            if "Type O Negative" in p["title"] or "Rammstein" in p["title"] or "Gojira" in p["title"]:
                target_product = p
                break
        
        if target_product:
            product = target_product
        else:
            product = random.choice(products)
    else:
        print("HATA: products.json bulunamadi!")
        exit(1)
        
    print("=" * 50)
    print("AI COMPOSITING SİSTEMİ TESTİ")
    print("=" * 50)
    print(f"\n  Secilen Urun: {product['title']}")
    
    result = create_composite_poster(product)
    
    if result:
        print(f"\n  Sonucu gormek icin ac: {result}")
    else:
        print("\n  Test basarisiz oldu.")
