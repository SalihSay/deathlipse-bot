import json
import random

with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

tshirts = [p for p in products if 't-shirt' in p.get('title', '').lower() or 'tee' in p.get('title', '').lower()]
print(f'Total t-shirts: {len(tshirts)}')
if tshirts:
    chosen = random.choice(tshirts)
    print("Chosen:", chosen['title'])
    print("ID:", chosen['id'])
