"""
prompt_generator.py
Printify urun bilgilerinden metal estetiginde AI video promptu ve
sosyal medya caption'i otomatik uretir.
Groq API kullanir (ucretsiz, 14.400 istek/gun) — Gemini fallback.
"""
import os
import random
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def _call_llm(prompt_text):
    """Groq ile LLM cagrisi yap, olmazsa Gemini dene."""

    # --- GROQ (Birincil, Ucretsiz 14.400 istek/gun) ---
    if GROQ_API_KEY and "BURAYA" not in GROQ_API_KEY:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt_text}],
                    "temperature": 0.9,
                    "max_tokens": 300,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            else:
                print(f"  Groq hata {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"  Groq baglanti hata: {e}")

    # --- GEMINI (Yedek) ---
    if GEMINI_API_KEY and "BURAYA" not in GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            r = client.models.generate_content(
                model="gemini-2.0-flash", contents=prompt_text
            )
            return r.text.strip()
        except Exception as e:
            print(f"  Gemini hata: {e}")

    # --- Son care: hazir prompt ---
    return None


def generate_video_prompt(product_title, product_type="t-shirt"):
    """
    Urun icin sinematik, metal estetiginde AI video promptu uret.
    Kling AI, fal.ai ve wavespeed.ai ile uyumlu format.
    """
    style_variants = [
        "black metal / dark forest aesthetic",
        "industrial metal / dystopian forge aesthetic",
        "death metal / occult dark altar aesthetic",
        "doom metal / slow cinematic dread aesthetic",
        "thrash metal / underground gritty rawness aesthetic",
    ]
    camera_moves = [
        "slow dolly-in from behind",
        "low-angle sweeping crane shot upward",
        "handheld push-in circling the subject",
        "extreme macro pull-back reveal",
        "slow orbit 180 degrees around subject",
    ]

    chosen_style = random.choice(style_variants)
    chosen_camera = random.choice(camera_moves)

    prompt_text = f"""You are a cinematic director for a dark heavy metal merchandise brand called DEATHLIPSE.

Create a short AI video generation prompt for this product:
- Product: {product_title}
- Type: {product_type}
- Style: {chosen_style}
- Camera: {chosen_camera}

STRICT RULES:
1. The {product_type} must be the VISUAL CENTERPIECE - clearly visible
2. Atmosphere: dark, raw, authentic - NOT commercial or glossy
3. Include: specific lighting (practical/chiaroscuro/moody), atmosphere (smoke/embers/rain/mist), film texture (35mm grain)
4. 9:16 vertical format, 5-7 seconds
5. DO NOT use: white background, studio, 360 spin, CGI look
6. USE: handheld texture, natural imperfections, organic movement

Return ONLY the prompt text. No intro. Max 100 words."""

    result = _call_llm(prompt_text)

    if result:
        return result

    # Fallback — LLM yoksa hazir prompt
    fallbacks = [
        (f"Cinematic slow reveal of a {product_type} with dark metal graphic. "
         f"Emerges from thick black smoke in stone underground chamber. "
         f"Low-angle handheld shot, chiaroscuro lighting — cold blue above, deep crimson below. "
         f"Embers drift upward. 35mm film grain, gothic heavy metal aesthetic. 9:16 vertical."),
        (f"A {product_type} rests on rain-soaked cobblestones under a single harsh streetlight at night. "
         f"Slow push-in from extreme close-up of fabric texture to full reveal. "
         f"Fog rolls in from behind. Desaturated, high contrast, gritty underground metal feel. "
         f"Handheld shake, 35mm grain. 9:16 vertical."),
        (f"Extreme macro shot of {product_type} design detail, camera pulls back slowly "
         f"revealing full garment floating in swirling black smoke and red ember sparks. "
         f"Industrial forge background, molten metal glow, harsh shadows. "
         f"Cinematic, dark, powerful. 9:16 vertical format."),
    ]
    return random.choice(fallbacks)


def generate_caption(product_title, product_type, price):
    """
    Instagram ve TikTok icin metal estetiginde caption uret.
    Satin alma yonelimli ama satici hissettirmeyen, otantik ton.
    """
    tone_variants = [
        "dark poetry / existential — speak to the void",
        "aggressive / battle-cry — for the warriors",
        "underground identity / us vs them — true metal only",
        "ritual / occult — ancient and sacred",
        "raw authenticity / anti-mainstream — real over commercial",
    ]
    chosen_tone = random.choice(tone_variants)

    prompt_text = f"""You are the voice behind DEATHLIPSE, a metal merchandise brand for true underground metal fans.

Write an Instagram/TikTok caption for:
- Product: {product_title}
- Type: {product_type}
- Price: ${price:.2f}
- Tone: {chosen_tone}

RULES:
1. 3-4 lines MAX. Short. Punchy. Powerful.
2. Line 1: Emotional hook — pure feeling, NO product name
3. Line 2: Subtle lifestyle connection or identity statement
4. Line 3: Simple CTA like "Shop link in bio 🔗" or "Link in bio. You know what to do."
5. Then blank line, then 18-20 hashtags (metal subgenres + merch + lifestyle + niche community)
6. MAX 2 emojis total. Sound like a metalhead, NOT a marketer.

Return ONLY caption + hashtags. Nothing else."""

    result = _call_llm(prompt_text)

    if result:
        return result

    # Fallback captions
    fallbacks = [
        (f"Not merch. A statement.\n"
         f"This is what you wear when you've stopped pretending.\n"
         f"Link in bio. You know what to do. 🔗\n\n"
         f"#MetalMerch #HeavyMetal #MetalHead #BlackMetal #DeathMetal #ThrashMetal "
         f"#MetalFashion #MetalWear #UndergroundMetal #MetalCommunity #MetalLifestyle "
         f"#DarkAesthetic #MetalShirt #MetalHoodie #EtsyMetal #MetalGifts "
         f"#GothicFashion #MetalScene #TrueHeavyMetal #MetalClothing"),
        (f"Forged. Not manufactured.\n"
         f"Some wear it. Others earn it.\n"
         f"Shop link in bio 🔗\n\n"
         f"#MetalMerch #UndergroundMetal #HeavyMetal #MetalHead #BlackMetal "
         f"#DeathMetal #MetalWear #MetalCommunity #DarkFashion #MetalLifestyle "
         f"#MetalShirt #MetalHoodie #EtsySeller #MetalGear #GothicStyle "
         f"#MetalScene #MetalArt #TrueHeavyMetal #MetalBand #MetalDesign"),
    ]
    return random.choice(fallbacks)


def test_generators():
    """API baglantisini ve uretimi test et"""
    import sys
    # Windows terminal encoding duzelt
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("LLM API test ediliyor...\n")

    test_products = [
        ("Rammstein Metal Band T-Shirt | Concert Merch", "t-shirt", 24.99),
        ("Rammstein Collage Hoodie | Gothic Red-Black", "hoodie", 54.99),
        ("Gojira Forditude Heavy Blend Hoodie", "hoodie", 49.99),
    ]

    for title, ptype, price in test_products:
        print("=" * 60)
        print(f"URUN: {title[:55]}")
        print("=" * 60)
        print("\n[VIDEO PROMPTU]")
        prompt = generate_video_prompt(title, ptype)
        print(prompt.encode("utf-8", errors="replace").decode("utf-8"))
        print("\n[CAPTION]")
        caption = generate_caption(title, ptype, price)
        print(caption.encode("utf-8", errors="replace").decode("utf-8"))
        print()


if __name__ == "__main__":
    test_generators()
