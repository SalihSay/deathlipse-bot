import requests, os, json
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("PRINTIFY_TOKEN")
SHOP_ID = os.getenv("PRINTIFY_SHOP_ID", "14366005")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Get product detail
url = f"https://api.printify.com/v1/shops/{SHOP_ID}/products/66115efe9c49a090f3094ea1.json"
resp = requests.get(url, headers=HEADERS, timeout=30)
product = resp.json()

# Show all images
images = product.get("images", [])
print(f"Total images in product images list: {len(images)}")
for i, img in enumerate(images):
    vids = img.get("variant_ids", [])
    is_def = img.get("is_default", False)
    pos = img.get("position", "?")
    src = img.get("src", "")
    print(f"  [{i}] position={pos} is_default={is_def} variant_ids_count={len(vids)} src_end=...{src[-60:]}")

print(f"\nProduct top-level keys: {list(product.keys())}")

# Save full product JSON for inspection
with open("debug_product_full.json", "w", encoding="utf-8") as f:
    json.dump(product, f, indent=2, ensure_ascii=False)
print("Full product JSON saved to debug_product_full.json")
