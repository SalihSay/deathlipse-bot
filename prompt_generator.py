import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

def generate_social_caption(product_title, price=""):
    """
    Groq kullanarak Instagram, Pinterest, TikTok ve Etsy için gerekli
    tüm SEO, açıklama ve AIDA formatındaki metinleri tek seferde JSON üretir.
    """
    if not NVIDIA_API_KEY:
        print("ERROR: NVIDIA_API_KEY is not set.")
        return generate_fallback(product_title)
        
    prompt = f"""
Sen Deathlipse'in pazarlama direktörüsün. 
Underground heavy metal apparel markası.
Ürün: {product_title}, Fiyat: {price}

Aşağıdaki JSON formatında içerik üret. 
SADECE geçerli bir JSON formatında metin döndür, markdown veya başka açıklama ekleme.
Yasaklı ifadeler: "Sınırlı sayıda üretildi", "Son X adet kaldı".
İzin verilen ifadeler: "Underground exclusive", "Not for everyone", "For the select few", "Limited drop".
CRITICAL REQUIREMENT: The entire output (all values in the JSON) MUST BE STRICTLY IN ENGLISH. The target audience is the USA. Do NOT output any Turkish words in the JSON values.

{{
  "hook": "3-4 words video hook. Directly address the metalhead identity. Use strong verbs.",
  
  "caption_a": "AGGRESSIVE TONE.\\nLine 1 (Attention): Address the metalhead identity, no hashtags/price.\\nLine 2 (Interest): Feeling of wearing it, include 'gothic fashion', 'metal aesthetic' or 'alternative clothing'.\\nLine 3 (Action): Clear CTA. 'Underground exclusive. Link in bio. 🖤'\\nEmpty line\\n15-18 hashtags (metal subgenre + merch + lifestyle + niche)",
    
  "caption_b": "DARK POETRY TONE.\\nSame AIDA structure but poetic and existential.\\nEx: 'Some are born to wear the night.'\\nSame CTA rules apply.",
    
  "pinterest": "3-4 sentences. SEO focused. Embed 'alternative metal clothing', 'gothic band tshirt gift for him', 'heavy metal fashion aesthetic', 'dark aesthetic clothing' naturally. Last sentence: 'Shop the Deathlipse collection on Etsy.' No hashtags.",
    
  "etsy_title": "Max 140 chars. Strongest SEO words front. 3-4 keyword clusters split by |.",
    
  "etsy_tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
    
  "etsy_description": "First 160 chars for Google snippet (most important info). Total 150-200 words. SEO focused but readable."
}}
"""
    for attempt in range(3):
        try:
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "Llama-4 Maverick",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a senior marketing director for an underground metal brand. You only output strict, minified JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if resp.status_code == 200:
                response_text = resp.json()["choices"][0]["message"]["content"]
                
                # Clean markdown backticks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1]
                if "```" in response_text:
                    response_text = response_text.split("```")[0]
                    
                data = json.loads(response_text.strip(), strict=False)
                return data
            else:
                print(f"NVIDIA API Error: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"API Error on attempt {attempt+1}: {e}")
            
    print("All attempts failed. Returning fallback.")
    return generate_fallback(product_title)

def generate_fallback(product_title):
    return {
        "hook": "Embrace the Darkness",
        "caption_a": f"Unleash the darkness. Wear the night.\n\nEmbrace your metal aesthetic with the {product_title}.\nUnderground exclusive. Link in bio. 🖤\n\n#heavymetal #metalhead #deathmetal #blackmetal #goth #metalmerch #altfashion",
        "caption_b": f"Some are born to wear the night.\n\nLet the {product_title} speak for your soul.\nUnderground exclusive. Link in bio. 🖤\n\n#darkaesthetic #gothfashion",
        "pinterest": f"Discover the {product_title} from Deathlipse. Perfect for your dark aesthetic and heavy metal wardrobe. High-quality alternative clothing and goth fashion. Shop the Deathlipse collection on Etsy.",
        "etsy_title": f"{product_title} | Gothic Clothing | Heavy Metal Merch | Alt Fashion",
        "etsy_tags": ["heavy metal", "goth clothing", "alt fashion", "metalhead gift", "dark aesthetic", "band merch", "punk rock", "grunge", "emo", "skater", "streetwear", "underground", "macabre"],
        "etsy_description": f"The ultimate {product_title} for those who walk in the shadows. Made with premium materials for maximum comfort and darkness. Shop now."
    }

if __name__ == "__main__":
    # Test
    print(json.dumps(generate_social_caption("Motorhead Skull Hoodie", "$45.00"), indent=2))
