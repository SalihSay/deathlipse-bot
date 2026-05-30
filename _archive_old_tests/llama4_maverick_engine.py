import os
import requests
import json
import base64
from dotenv import load_dotenv
import re

load_dotenv()
NVIDIA_API_KEY = "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"
MODEL_ID = "meta/llama-4-maverick-17b-128e-instruct"

def download_and_encode_image(image_url):
    """Downloads an image from a URL and returns its base64 encoding."""
    try:
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            encoded_string = base64.b64encode(response.content).decode("utf-8")
            # Usually we need data URI format for image content, but Nvidia / OpenAI API typically takes data:image/png;base64,...
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def analyze_product_with_llama4(product_title, image_url):
    """
    Uses Llama-4 Maverick Multimodal to analyze the image and write US-targeted SEO.
    Returns a dictionary with title, tags, description, and social_caption.
    """
    print(f"[LLAMA-4] Fetching image for analysis: {product_title}")
    b64_image = download_and_encode_image(image_url)
    
    if not b64_image:
        print("[LLAMA-4] Could not get image. Proceeding with text-only.")
        image_content = []
    else:
        image_content = [{"type": "image_url", "image_url": {"url": b64_image}}]

    system_prompt = """
    You are an elite American e-commerce SEO expert and Heavy Metal cultural historian. 
    You are writing product listings for an underground heavy metal apparel brand named "DEATHLIPSE" targeting the US market.
    
    CRITICAL INSTRUCTIONS:
    1. Look at the provided product image. Identify the exact band name, logo, album art, or specific subgenre (e.g., "Type O Negative", "Megadeth Dystopia", "Rammstein").
    2. COPYRIGHT EVASION (CRITICAL): Etsy bots will ban the store if you use exact trademarked band names. You MUST obfuscate the band name ONLY IN THE TITLE by using simple spacing or hyphenation (e.g., "Ramm stein", "Mega-deth", "Slip knot"). DO NOT use dots, acronyms, or weird punctuation. It must look like a natural typo or stylistic choice so it remains professional.
    3. TAGS RULE: NEVER use the actual band name in the 13 tags. Use subgenres, decades, and aesthetic terms instead (e.g., "90s Industrial Metal", "German Rock Band", "Goth Clothing", "Y2K Grunge").
    4. Write completely in NATIVE AMERICAN ENGLISH. No Turkish.
    5. Generate EXACTLY 13 SEO Tags. These must be highly searched long-tail keywords on Etsy USA.
    6. Write a compelling, dark, and aggressive product description. Include the band's legacy or the aesthetic's vibe without repeatedly triggering the copyright name. Keep it under 200 words.
    7. Write a short, punchy social media caption (Instagram/TikTok style) with 10 hashtags.
    
    OUTPUT FORMAT: You must return ONLY a raw JSON object and nothing else. No markdown formatting, no code blocks.
    {
      "title": "Optimized Etsy Title Here (Obfuscated Band Name)",
      "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
      "description": "Full HTML or plain text product description here...",
      "social_caption": "Caption here... #hashtags"
    }
    """

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }

    # Assemble the content array
    user_content = [{"type": "text", "text": f"Product Title from supplier: {product_title}. Analyze the image and provide the JSON."}]
    user_content.extend(image_content)

    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.4,
        "max_tokens": 1024
    }

    print("[LLAMA-4] Sending multimodal request to Nvidia NIM...")
    try:
        resp = requests.post("https://integrate.api.nvidia.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            result_text = resp.json()["choices"][0]["message"]["content"].strip()
            
            # Clean up the output in case the model adds markdown code blocks like ```json ... ```
            result_text = re.sub(r"^```json\s*", "", result_text)
            result_text = re.sub(r"\s*```$", "", result_text)
            
            return json.loads(result_text)
        else:
            print(f"[LLAMA-4] API Error: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"[LLAMA-4] Exception occurred: {e}")
        return None
