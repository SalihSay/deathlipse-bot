import json, requests, time

with open('etsy_listings_raw.json', 'r', encoding='utf-8') as f:
    listings = json.load(f)

with open('etsy_token.json', 'r') as f:
    token_info = json.load(f)

ACCESS_TOKEN = token_info['access_token']
API_KEY = 'gqnem32usqjmqjaeg0adl0ly'
SHARED_SECRET = 'zrgxhvnrra'
SHOP_ID = '39610840'

HEADERS = {
    'x-api-key': f'{API_KEY}:{SHARED_SECRET}',
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}

def optimize_listing(listing):
    orig_title = listing['title']
    orig_desc = listing['description']
    orig_tags = listing.get('tags', [])
    
    title_lower = orig_title.lower()
    desc_lower = orig_desc.lower()
    
    # Determine type
    is_hoodie = 'hoodie' in title_lower or 'sweatshirt' in title_lower or 'pullover' in title_lower
    is_tee = 't-shirt' in title_lower or 'tee' in title_lower or 'shirt' in title_lower or 'tank top' in title_lower
    is_mug = 'mug' in title_lower or 'cup' in title_lower
    is_shoes = 'sneaker' in title_lower or 'shoes' in title_lower
    is_bag = 'bag' in title_lower or 'tote' in title_lower
    
    # 1. Optimize Title (Max 140 chars)
    # Keep the core subject from original title
    core_name = orig_title.split('|')[0].split(',')[0].strip()
    
    suffixes = []
    if is_hoodie:
        suffixes = ["Gothic Pullover", "Metalhead Hoodie", "Alt Fashion Sweatshirt", "Dark Art Clothing", "Heavy Metal Gift"]
    elif is_tee:
        suffixes = ["Gothic Graphic Tee", "Metalhead Shirt", "Alt Fashion Top", "Dark Art Apparel", "Heavy Metal Gift"]
    elif is_mug:
        suffixes = ["Gothic Coffee Cup", "Metalhead Kitchen", "Dark Home Decor", "Occult Mug", "Heavy Metal Gift"]
    elif is_shoes:
        suffixes = ["Gothic Canvas Shoes", "Alternative Footwear", "Punk Rock Sneakers", "Dark Aesthetics"]
    elif is_bag:
        suffixes = ["Gothic Canvas Bag", "Alternative Tote", "Dark Art Carryall", "Metalhead Accessory"]
    else:
        suffixes = ["Gothic Dark Art", "Alternative Gift", "Metalhead Merch", "Heavy Metal Style"]
    
    new_title = core_name
    for suf in suffixes:
        if len(new_title) + len(suf) + 3 <= 140:
            new_title += f" | {suf}"
            
    # 2. Optimize Description
    new_desc = f"🖤 {core_name.upper()} 🖤\n\n"
    new_desc += "Unleash your inner darkness with this premium piece from Deathlipse. "
    if is_hoodie:
        new_desc += "Wrap yourself in the comfort of shadows. This heavy blend hoodie is perfect for cold concert nights, festivals, or just embodying the alternative lifestyle daily.\n\n"
    elif is_tee:
        new_desc += "A statement piece for your dark wardrobe. This soft, durable graphic tee is perfect for the pit, everyday alternative fashion, or expressing your unique metalhead identity.\n\n"
    elif is_mug:
        new_desc += "Drink your morning brew black as your soul. This premium mug brings gothic elegance and metal attitude right to your kitchen.\n\n"
    elif is_shoes:
        new_desc += "Step into the abyss. These striking sneakers are built for those who walk their own path in the underground scene.\n\n"
    else:
        new_desc += "Elevate your dark aesthetic with this meticulously designed item, crafted for the bold and unapologetic.\n\n"
        
    new_desc += "✦ WHY YOU'LL LOVE IT:\n"
    new_desc += "• Exclusive Dark Art Design — Stand out in the underground scene\n"
    new_desc += "• Premium Quality — Built to survive the mosh pit and beyond\n"
    new_desc += "• Perfect Gift — The ultimate present for the metalhead, goth, or alt-fashion lover in your life\n\n"
    
    new_desc += "✦ ABOUT DEATHLIPSE:\n"
    new_desc += "Deathlipse isn't just a brand; it's a movement for those who find beauty in the darkness. From heavy metal to gothic horror, we create gear for the unapologetic.\n\n"
    
    # Retain the original description at the bottom for any sizing/material info
    new_desc += "---\nPRODUCT DETAILS:\n" + orig_desc.strip()
    
    # 3. Optimize Tags (Max 13 tags, strictly <= 20 chars)
    base_tags = ["gothic clothing", "metalhead gift", "dark art", "alt fashion", "heavy metal", "occult aesthetic"]
    if is_hoodie: base_tags.extend(["goth hoodie", "metal sweatshirt", "alt pullover"])
    elif is_tee: base_tags.extend(["goth graphic tee", "metal shirt", "punk rock tee"])
    elif is_mug: base_tags.extend(["goth home decor", "morbid mug", "witchy gift"])
    elif is_shoes: base_tags.extend(["goth sneakers", "punk shoes", "alt footwear"])
    
    # Extract important words from core name
    words = [w.strip() for w in core_name.split() if 3 < len(w.strip()) <= 20]
    base_tags.extend(words)
    
    final_tags = []
    seen = set()
    # Add prioritized base tags, then backfill with original tags
    for t in base_tags + orig_tags:
        t_clean = str(t).lower().strip()[:20]
        if len(t_clean) > 2 and t_clean not in seen and len(final_tags) < 13:
            final_tags.append(t_clean)
            seen.add(t_clean)
            
    return new_title, new_desc, final_tags

def main():
    print(f"==================================================")
    print(f"DEATHLIPSE ETSY OPTIMIZER - AUTO RUN")
    print(f"Processing {len(listings)} listings from etsy_listings_raw.json")
    print(f"==================================================\n")
    
    success = 0
    failed = 0
    
    for i, listing in enumerate(listings):
        lid = listing['listing_id']
        title, desc, tags = optimize_listing(listing)
        
        url = f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}"
        
        data = {
            "title": title,
            "description": desc
        }
        for j, tag in enumerate(tags):
            data[f"tags[{j}]"] = tag
            
        print(f"[{i+1}/{len(listings)}] Updating: {title[:60]}...")
        resp = requests.patch(url, headers=HEADERS, data=data)
        
        if resp.status_code == 200:
            print(f"  SUCCESS")
            success += 1
        else:
            print(f"  FAILED ({resp.status_code}): {resp.text[:200]}")
            failed += 1
            
        time.sleep(0.5) # respect rate limit
        
    print(f"\n==================================================")
    print(f"OPTIMIZATION COMPLETE")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"==================================================")

if __name__ == "__main__":
    main()
