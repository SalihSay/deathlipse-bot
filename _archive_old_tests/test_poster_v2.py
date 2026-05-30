"""
test_poster_v2.py
Google Imagen 4.0 + Kategori Bazli Akilli Poster Sistemi
Her urun kategorisi icin farkli, profesyonel bir reklam goerseli uretir.
"""
import os
import io
import json
import random
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# KATEGORI BAZLI PROMPT SABLONLARI
# Her urun tipi icin farkli sahne ve ortam
# ==========================================
CATEGORY_PROMPTS = {
    "t-shirt": [
        "A premium {color} t-shirt with the design '{design}' printed on the chest, laid flat on a dark wooden table, surrounded by guitar picks, vinyl records, and dim candles. Dramatic top-down product photography, moody warm lighting, shallow depth of field, 8k ultra detailed, professional e-commerce photo",
        "A {color} t-shirt with '{design}' artwork, hanging on a matte black hanger against a dark textured brick wall in a dimly lit music studio. Red and amber accent lighting, smoke atmosphere, professional fashion photography, 8k",
    ],
    "hoodie": [
        "A premium {color} hoodie with '{design}' artwork on the front, draped over a weathered leather chair in a dark industrial loft. Exposed brick walls, warm Edison bulb lighting, vinyl record player in the background. Professional lifestyle product photography, cinematic mood, 8k ultra detailed",
        "A {color} hoodie with '{design}' printed design, hanging on a rustic metal hook against a concrete wall in an underground music venue. Neon signs glowing in the background, moody atmosphere, professional product photo, 8k",
    ],
    "poster": [
        "A framed art print of '{design}' hanging on a dark charcoal wall in a stylish modern living room. Leather couch, dim ambient lighting, vinyl record collection visible on shelves. Interior design magazine photography style, warm tones, 8k ultra detailed",
        "A large canvas print of '{design}' displayed on an easel in a modern art gallery with spotlights. Dark walls, gallery lighting focused on the artwork, reflective floor. Professional art exhibition photography, 8k",
    ],
    "mug": [
        "A premium black ceramic mug with '{design}' artwork, sitting on a dark oak desk next to an open book and a burning candle. Steam rising from hot coffee inside. Moody warm lighting, shallow depth of field, professional product photography, 8k ultra detailed",
        "A {color} ceramic mug featuring '{design}', placed on a rustic wooden coaster on a dark granite kitchen counter. Morning light streaming through a window, cozy atmosphere, professional food photography style, 8k",
    ],
    "tote bag": [
        "A {color} canvas tote bag with '{design}' print, casually placed on a wooden bench in an urban street setting. Graffiti wall in the background, golden hour lighting, street fashion photography, 8k ultra detailed",
    ],
    "sweatshirt": [
        "A premium {color} crewneck sweatshirt with '{design}' graphic, folded neatly on a dark surface with headphones and a concert ticket beside it. Atmospheric lighting, smoke effects, professional flat lay photography, 8k",
    ],
}

def detect_category(title):
    """Urun basligindan kategoriyi tespit et"""
    title_lower = title.lower()
    if "hoodie" in title_lower:
        return "hoodie"
    elif "sweatshirt" in title_lower or "crewneck" in title_lower:
        return "sweatshirt"
    elif "mug" in title_lower or "cup" in title_lower:
        return "mug"
    elif "poster" in title_lower or "wall" in title_lower or "canvas" in title_lower or "print" in title_lower or "art" in title_lower:
        return "poster"
    elif "tote" in title_lower or "bag" in title_lower:
        return "tote bag"
    else:
        return "t-shirt"

def detect_color(title):
    """Urun basligindan rengi tespit et"""
    title_lower = title.lower()
    colors = ["black", "white", "red", "blue", "navy", "gray", "grey", "green", "charcoal"]
    for c in colors:
        if c in title_lower:
            return c
    return "black"

def extract_design_name(title):
    """Urun basligindan tasarim/band adini cek"""
    # Ornegin: "Gojira Metal Band T-Shirt" -> "Gojira"
    # Ornegin: "Black T-Shirt with Lilith Tarot Card Print" -> "Lilith Tarot Card"
    stopwords = ["t-shirt", "tee", "hoodie", "sweatshirt", "mug", "poster", "print", 
                 "canvas", "wall art", "tote bag", "unisex", "premium", "black", "white",
                 "softstyle", "with", "the", "a", "an", "band", "metal", "rock"]
    words = title.split()
    design_words = [w for w in words if w.lower().strip(",") not in stopwords]
    return " ".join(design_words[:4]) if design_words else title[:20]


def generate_poster_with_imagen(product_title, output_path="test_poster_v2_result.png"):
    """
    Google Imagen 4.0 ile urun kategorisine gore profesyonel reklam posteri uret.
    %100 ucretsiz, kota limiti cok yuksek (gunluk 500+ istek).
    """
    category = detect_category(product_title)
    color = detect_color(product_title)
    design = extract_design_name(product_title)
    
    print(f"  Urun Kategorisi: {category.upper()}")
    print(f"  Tespit Edilen Renk: {color}")
    print(f"  Tasarim Adi: {design}")
    
    # Kategoriye uygun rastgele bir prompt sec
    templates = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS["t-shirt"])
    template = random.choice(templates)
    prompt = template.format(color=color, design=design)
    
    print(f"\n  Olusturulan Prompt: {prompt[:120]}...")
    print(f"\n  Google Imagen 4.0 ile gorsel uretiliyor...")
    
    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )
        
        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_bytes))
            image.save(output_path)
            size_kb = len(image_bytes) / 1024
            print(f"\n  BASARILI! Gorsel kaydedildi: {output_path} ({size_kb:.0f} KB)")
            return output_path
        else:
            print("  HATA: Imagen gorsel uretemedi.")
            return None
            
    except Exception as e:
        print(f"  HATA: {e}")
        return None


if __name__ == "__main__":
    # Gercek bir urun adi ile test
    # Printify cache dosyasindan rastgele bir urun sec
    cache_path = Path("assets/products.json")
    if cache_path.exists():
        products = json.loads(cache_path.read_text(encoding="utf-8"))
        product = random.choice(products)
        title = product["title"]
    else:
        title = "Black T-Shirt with Lilith Tarot Card Print"
    
    print("=" * 50)
    print("IMAGEN 4.0 POSTER TESTI")
    print("=" * 50)
    print(f"\n  Secilen Urun: {title}")
    
    result = generate_poster_with_imagen(title)
    
    if result:
        print(f"\n  Sonucu gormek icin ac: {result}")
    else:
        print("\n  Test basarisiz oldu.")
