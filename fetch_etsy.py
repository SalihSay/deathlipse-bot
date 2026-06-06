import json, requests

with open('etsy_token.json', 'r') as f:
    token_info = json.load(f)

access_token = token_info['access_token']
API_KEY = 'gqnem32usqjmqjaeg0adl0ly'
SHARED_SECRET = 'zrgxhvnrra'
SHOP_ID = '39610840'

headers = {
    'x-api-key': f'{API_KEY}:{SHARED_SECRET}',
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# Get all active listings
url = f'https://openapi.etsy.com/v3/application/shops/{SHOP_ID}/listings/active?limit=100'
resp = requests.get(url, headers=headers)
print(f'Status: {resp.status_code}')

if resp.status_code == 200:
    data = resp.json()
    count = data.get("count", 0)
    print(f'Total listings: {count}')
    
    results = data.get('results', [])
    # Save full data for analysis
    with open('etsy_listings_raw.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    for listing in results:
        lid = listing["listing_id"]
        title = listing["title"]
        tags = listing.get("tags", [])
        state = listing.get("state", "")
        url_l = listing.get("url", "")
        desc = listing.get("description", "")[:150]
        print('---')
        print(f'ID: {lid}')
        print(f'Title: {title}')
        print(f'Tags: {tags}')
        print(f'State: {state}')
        print(f'Desc preview: {desc}...')
        print(f'URL: {url_l}')
        
        # Get images for this listing
        img_url = f'https://openapi.etsy.com/v3/application/listings/{lid}/images'
        img_resp = requests.get(img_url, headers=headers)
        if img_resp.status_code == 200:
            images = img_resp.json().get('results', [])
            for img in images[:1]:
                print(f'  Image: {img.get("url_570xN", "")}')
    
    print(f'\nSaved {len(results)} listings to etsy_listings_raw.json')
else:
    print(f'Error: {resp.text}')
