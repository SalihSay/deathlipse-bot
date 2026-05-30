import os
import csv
import sys
import time
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID", "")

# Zernio API (TikTok + Pinterest + Instagram)
ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY", "")
ZERNIO_TIKTOK_ACCOUNT_ID = os.getenv("ZERNIO_TIKTOK_ACCOUNT_ID", "")
ZERNIO_INSTAGRAM_ACCOUNT_ID = os.getenv("ZERNIO_INSTAGRAM_ACCOUNT_ID", "")

CSV_FILE = "bulk_schedule.csv"

def upload_to_catbox(file_path):
    """Dosyayı catbox.moe'ye yükler ve public URL döner."""
    print(f"Uploading to catbox.moe: {file_path}")
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        data = {"reqtype": "fileupload"}
        try:
            resp = requests.post(url, data=data, files=files)
            if resp.status_code == 200 and resp.text.startswith("https://files.catbox.moe/"):
                url_view = resp.text.strip()
                print(f"Upload success! Public URL: {url_view}")
                return url_view
            else:
                print(f"Upload failed. Status: {resp.status_code}, Response: {resp.text}")
        except Exception as e:
            print("Upload exception:", e)
    return None

def post_to_zernio(text, media_path, platforms_config, media_type="image"):
    """Zernio API üzerinden sosyal medyaya gönderi atar.
    
    platforms_config: [{"platform": "tiktok", "accountId": "xxx"}, ...]
    media_type: "image" veya "video"
    """
    if not ZERNIO_API_KEY:
        print("[!] ZERNIO_API_KEY eksik.")
        return False
    
    # Dosyayı catbox'a yükle
    media_url = upload_to_catbox(media_path)
    if not media_url:
        print("Media yükleme başarısız, atlanıyor.")
        return False
    
    url = "https://zernio.com/api/v1/posts"
    headers = {
        "Authorization": f"Bearer {ZERNIO_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": text,
        "platforms": platforms_config,
        "mediaItems": [{"type": media_type, "url": media_url}],
        "publishNow": True
    }
    
    platform_names = [p["platform"] for p in platforms_config]
    print(f"Posting to Zernio on platforms {platform_names}...")
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            print(f"Zernio: Başarıyla yayınlandı! ({platform_names})")
            return True
        else:
            print(f"Zernio post failed. Status: {resp.status_code}, Response: {resp.text}")
    except Exception as e:
        print("Zernio API exception:", e)
    return False

def post_to_make_webhook(text, media_path):
    """Make.com webhook'una Instagram için gönderi atar."""
    webhook_url = "https://hook.eu1.make.com/g7x2lrnd8dm7vcz5cf670ygoutfxltc8"
    
    # Dosyayı catbox'a yükle
    media_url = upload_to_catbox(media_path)
    if not media_url:
        print("Make Webhook: Media yükleme başarısız, atlanıyor.")
        return False
        
    payload = {
        "caption": text,
        "video_url": media_url,
        "media_url": media_url # her ihtimale karşı ikisini de gönderiyoruz
    }
    
    print("Posting to Make.com Webhook (Instagram)...")
    try:
        resp = requests.post(webhook_url, json=payload)
        if resp.status_code in [200, 201, 202]:
            print("Make Webhook: Başarıyla gönderildi!")
            return True
        else:
            print(f"Make Webhook failed. Status: {resp.status_code}, Response: {resp.text}")
    except Exception as e:
        print("Make Webhook exception:", e)
    return False


def get_next_pending_post():
    if not os.path.isfile(CSV_FILE):
        return None, -1
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    for i in range(1, len(reader)):
        row = reader[i]
        while len(row) < 6:
            row.append("PENDING")
        if row[5] not in ["PUBLISHED", "SKIPPED"]:
            return row, i
    return None, -1

def update_csv_status(index, status):
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    while len(reader[index]) < 6:
        reader[index].append("PENDING")
    reader[index][5] = status
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for r in reader:
            writer.writerow(r)

async def check_for_posts(context: ContextTypes.DEFAULT_TYPE):
    row, index = get_next_pending_post()
    if not row:
        print("No pending posts right now.")
        return
        
    if len(row) >= 5 and ".mp4" in row[3]:
        # 5 kolonlu format (IG Text, Pin Text, Image, Video, URL)
        ig_text = row[0]
        pin_text = row[1]
        img_file = f"bulk_images/{row[2]}"
        vid_file = f"reels_output/{row[3]}"
        product_url = row[4] if len(row) > 4 else "URL Yok"
    else:
        # 3 kolonlu format (Text, Image, URL)
        ig_text = row[0]
        pin_text = row[0]  # Aynı metni kullan
        img_file = f"bulk_images/{row[1]}"
        vid_file = ""  # Video yok
        product_url = row[2] if len(row) > 2 else "URL Yok"
    
    message_text = f"🚨 YENİ GÖNDERİ ONAY BEKLİYOR 🚨\n\n"
    message_text += f"🛍️ Ürün Linki: {product_url}\n\n"
    message_text += f"📝 IG/TikTok Metni:\n{ig_text}\n\n"
    message_text += f"📝 Pinterest Metni:\n{pin_text}\n\n"
    message_text += "👆 Kararınız: Aşağıdan Onaylayın veya Atlayın."

    keyboard = [
        [InlineKeyboardButton("✅ Onayla ve Yayınla (Publish)", callback_data=f"approve_{index}")],
        [InlineKeyboardButton("❌ İptal Et ve Atla (Skip)", callback_data=f"skip_{index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Önce Reels videosunu önizleme için gönder (sunucudaki dosyadan)
        if vid_file and os.path.exists(vid_file):
            with open(vid_file, 'rb') as video:
                await context.bot.send_video(chat_id=TELEGRAM_GROUP_ID, video=video)
        elif img_file and os.path.exists(img_file):
            with open(img_file, 'rb') as image:
                await context.bot.send_photo(chat_id=TELEGRAM_GROUP_ID, photo=image)
        
        # Sonra metinleri ve butonları yolla
        await context.bot.send_message(
            chat_id=TELEGRAM_GROUP_ID, 
            text=message_text, 
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Failed to send to Telegram: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    action, index_str = data.split('_')
    index = int(index_str)
    
    # Güncel row oku
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        
    if index >= len(reader):
        await query.edit_message_text("Hata: Post bulunamadı.")
        return
        
    row = reader[index]
    if len(row) >= 6 and row[5] in ["PUBLISHED", "SKIPPED"]:
        await query.edit_message_text("Bu gönderi zaten işlenmiş.")
        return
        
    if len(row) >= 5 and ".mp4" in row[3]:
        ig_text = row[0]
        pin_text = row[1]
        img_file = f"bulk_images/{row[2]}"
        vid_file = f"reels_output/{row[3]}"
    else:
        ig_text = row[0]
        pin_text = row[0]
        img_file = f"bulk_images/{row[1]}"
        vid_file = ""
        
    if action == "skip":
        update_csv_status(index, "SKIPPED")
        await query.edit_message_text("❌ Gönderi atlandı (Skipped). Yeni gönderi getiriliyor...")
        await check_for_posts(context)
        
    elif action == "approve":
        await query.edit_message_text("⏳ Yayınlanıyor... Lütfen bekleyin...")
        
        # ===== TikTok (Video) -> Zernio =====
        success_tiktok = False
        if vid_file and os.path.exists(vid_file):
            tiktok_config = [{"platform": "tiktok", "accountId": ZERNIO_TIKTOK_ACCOUNT_ID}]
            success_tiktok = post_to_zernio(ig_text, vid_file, tiktok_config, "video")
        else:
            print("TikTok: Video dosyası bulunamadı, atlanıyor.")
        
        # ===== Instagram (Video) -> Zernio =====
        success_ig = False
        if vid_file and os.path.exists(vid_file):
            ig_config = [{"platform": "instagram", "accountId": ZERNIO_INSTAGRAM_ACCOUNT_ID}]
            success_ig = post_to_zernio(ig_text, vid_file, ig_config, "video")
        else:
            print("Instagram: Video bulunamadı, atlanıyor.")
        
        # Sonuç raporu
        results = []
        results.append("Instagram ✅" if success_ig else "Instagram ❌")
        results.append("TikTok ✅" if success_tiktok else "TikTok ❌")
        
        result_text = " | ".join(results)
        
        if success_ig or success_tiktok:
            update_csv_status(index, "PUBLISHED")
            await query.edit_message_text(f"Yayın Sonuçları:\n{result_text}")
        else:
            await query.edit_message_text(f"⚠️ Hiçbir platforma yayınlanamadı.\n{result_text}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Deathlipse Otomasyon Hub'ı Aktif! Ana sunucudan ayrık çalışıyor. Her 6 saatte bir onay postu atacak.")

def main():
    print("Starting Deathlipse Telegram Bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    job_queue = application.job_queue
    # Sunucu çalıştığında hemen test için 1 tane göndersin (5 sn sonra)
    job_queue.run_once(check_for_posts, 5)
    # Ardından her 6 saatte bir (21600 saniye) post onayı göndersin
    job_queue.run_repeating(check_for_posts, interval=21600, first=21600)
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
