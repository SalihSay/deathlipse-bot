import requests, os, json
from dotenv import load_dotenv
from prompt_generator import generate_social_caption

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_GROUP_ID')

print("Generating social caption with NVIDIA API...")
caption = generate_social_caption('Coffin Skeleton Printed T-Shirt', '15.99')

if type(caption) == str:
    try:
        data = json.loads(caption)
    except Exception as e:
        print("Failed to parse JSON:", caption)
        data = {}
else:
    data = caption

tags = ', '.join(data.get('etsy_tags', []))

msg = f"""🇺🇸 YENİ GÖNDERİ (NVIDIA MAVERICK TEST)

📌 *Ürün:* Coffin Skeleton Printed T-Shirt

📝 *Instagram / TikTok Caption:*
{data.get('caption_a', '')}

📌 *Pinterest:*
{data.get('pinterest', '')}

📌 *Etsy SEO:*
Title: {data.get('etsy_title', '')}
Tags: {tags}
Description: {data.get('etsy_description', '')}
"""

print("Sending to Telegram...")
video_path = 'reels_output/reel_1670982348.mp4'

reply_markup = {
    "inline_keyboard": [
        [
            {"text": "🔥 Yayınla (Caption A)", "callback_data": "approveA_0"},
            {"text": "💀 Yayınla (Caption B)", "callback_data": "approveB_0"}
        ],
        [
            {"text": "🔄 Yeniden Üret", "callback_data": "recreate_0"},
            {"text": "⏭ Atla", "callback_data": "skip_0"}
        ]
    ]
}

if os.path.exists(video_path):
    with open(video_path, 'rb') as f:
        response = requests.post(
            f'https://api.telegram.org/bot{TOKEN}/sendVideo',
            data={'chat_id': CHAT_ID, 'caption': msg[:1024], 'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)},
            files={'video': f}
        )
    print("Sent! Status Code:", response.status_code)
else:
    print(f"Video not found at {video_path}")
