import os, requests, json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('PRINTIFY_TOKEN')
SHOP_ID = os.getenv('PRINTIFY_SHOP_ID', '14366005')

url = f'https://api.printify.com/v1/shops/{SHOP_ID}/products.json?limit=100'
headers = {'Authorization': f'Bearer {TOKEN}'}
resp = requests.get(url, headers=headers).json()

for p in resp.get('data', []):
    if 'Rammstein' in p['title']:
        print('\nPRODUCT:', p['title'])
        for i, img in enumerate(p['images']):
            pos = img.get('position')
            is_def = img.get('is_default')
            src = img.get('src')
            print(f"  {i}) Pos: {pos} | Default: {is_def} | SRC: {src}")
