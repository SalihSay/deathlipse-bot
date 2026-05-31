import os
import csv
import json
import time
import asyncio
import requests
from datetime import datetime, time as dt_time, timezone
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import video_generator

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID", "")

# Zernio API (TikTok + Pinterest)
ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY", "")
ZERNIO_TIKTOK_ACCOUNT_ID = os.getenv("ZERNIO_TIKTOK_ACCOUNT_ID", "")
ZERNIO_PINTEREST_ACCOUNT_ID = os.getenv("ZERNIO_PINTEREST_ACCOUNT_ID", "")

# Meta Graph API (Instagram Stories)
META_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
META_IG_USER_ID = os.getenv("META_IG_USER_ID", "")

CSV_FILE = "bulk_schedule.csv"
POSTED_JSON = "assets/posted_products.json"

def upload_to_catbox(file_path):
    print(f"Uploading to catbox.moe: {file_path}")
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        data = {"reqtype": "fileupload"}
        try:
            resp = requests.post(url, data=data, files=files)
            if resp.status_code == 200 and resp.text.startswith("https://files.catbox.moe/"):
                return resp.text.strip()
            print(f"Upload failed. Response: {resp.text}")
        except Exception as e:
            print("Upload exception:", e)
    return None

def post_to_meta_graph(story_image_path, product_url):
    if not META_ACCESS_TOKEN or not META_IG_USER_ID:
        print("[!] Meta API tokens missing.")
        return False
        
    image_url = upload_to_catbox(story_image_path)
    if not image_url:
        return False
        
    print("Posting Story to Meta Graph API...")
    # Step 1: Create Container
    container_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "media_type": "STORIES",
        "access_token": META_ACCESS_TOKEN
    }
    
    # Story link sticker parameter is strictly NOT supported by Instagram Graph API
    # so we rely on "Link in Bio" text instead.
    
    try:
        resp = requests.post(container_url, data=payload)
        data = resp.json()
        if "id" not in data:
            print(f"Container failed: {data}")
            return False
            
        creation_id = data["id"]
        # Step 2: Publish
        publish_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": META_ACCESS_TOKEN
        }
        pub_resp = requests.post(publish_url, data=publish_payload)
        pub_data = pub_resp.json()
        if "id" in pub_data:
            print(f"Meta Graph Story Published! ID: {pub_data['id']}")
            return True
        else:
            print(f"Publish failed: {pub_data}")
            return False
            
    except Exception as e:
        print("Meta Graph API exception:", e)
        return False

async def post_video_to_meta_graph_reels(video_path, caption):
    if not META_ACCESS_TOKEN or not META_IG_USER_ID:
        print("[!] Meta API tokens missing for Reels.")
        return False
        
    video_url = upload_to_catbox(video_path)
    if not video_url:
        return False
        
    print("Posting Reels to Meta Graph API...")
    container_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
    
    try:
        resp = requests.post(container_url, data=payload)
        data = resp.json()
        if "id" not in data:
            print(f"Reels Container failed: {data}")
            return False
            
        creation_id = data["id"]
        
        # Polling for processing completion
        status_url = f"https://graph.facebook.com/v19.0/{creation_id}?fields=status_code&access_token={META_ACCESS_TOKEN}"
        for _ in range(12):  # Max 60 seconds
            status_resp = requests.get(status_url)
            status_data = status_resp.json()
            if status_data.get("status_code") == "FINISHED":
                break
            elif status_data.get("status_code") == "ERROR":
                print(f"Reels processing error: {status_data}")
                return False
            await asyncio.sleep(5)
            
        # Publish
        publish_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": META_ACCESS_TOKEN
        }
        pub_resp = requests.post(publish_url, data=publish_payload)
        pub_data = pub_resp.json()
        if "id" in pub_data:
            print(f"Meta Graph Reels Published! ID: {pub_data['id']}")
            return True
        else:
            print(f"Reels Publish failed: {pub_data}")
            return False
    except Exception as e:
        print("Meta Reels exception:", e)
        return False

def post_to_zernio(text, media_path, platforms_config, media_type="video"):
    if not ZERNIO_API_KEY:
        return False
        
    media_url = upload_to_catbox(media_path)
    if not media_url:
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
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            return True
        print(f"Zernio post failed: {resp.text}")
    except Exception as e:
        print("Zernio API exception:", e)
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
        if row[5] == "PENDING":
            return row, i
    return None, -1

def update_status(index, status, product_id=""):
    # Update CSV
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    while len(reader[index]) < 6:
        reader[index].append("PENDING")
    reader[index][5] = status
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(reader)
        
    # Update JSON
    if product_id and os.path.exists(POSTED_JSON):
        try:
            with open(POSTED_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            if product_id in data:
                data[product_id]["status"] = status
                with open(POSTED_JSON, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
        except Exception as e:
            print("Failed to update posted_products.json:", e)

async def check_token_expiry(context: ContextTypes.DEFAULT_TYPE):
    # .env'den statik tarihi çek
    issue_date_str = os.getenv("META_TOKEN_ISSUE_DATE", "")
    
    if not issue_date_str:
        print("[!] META_TOKEN_ISSUE_DATE bulunamadı, token süresi takip edilemiyor.")
        return
        
    try:
        # Tarihi datetime objesine çevir (Örn: 2026-05-31)
        issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
        current_date = datetime.now()
        
        # Kaç gün geçmiş?
        days_elapsed = (current_date - issue_date).days
        days_left = 60 - days_elapsed
        
        if 0 < days_left <= 7:
            msg = f"⚠️ Meta API token'ın {days_left} gün içinde dolacak. Yenilemeniz gerekiyor."
            await context.bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=msg)
        elif days_left <= 0:
            msg = "❌ Meta API token'ın süresi doldu! Acilen yenilenmeli."
            await context.bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=msg)
    except Exception as e:
        print(f"Token date parsing exception: {e}")

async def check_for_posts(context: ContextTypes.DEFAULT_TYPE):
    row, index = get_next_pending_post()
    if not row:
        print("No pending posts right now.")
        return
        
    try:
        social_data = json.loads(row[0])
    except:
        social_data = {"caption_a": row[0]}
        
    pin_text = row[1]
    img_file = f"bulk_images/{row[2]}"
    vid_file = f"reels_output/{row[3]}"
    product_url = row[4]
    
    msg = "🎬 YENİ GÖNDERİ ONAY BEKLİYOR\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n📝 CAPTION A (Agresif):\n"
    msg += f"{social_data.get('caption_a', 'N/A')}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n📝 CAPTION B (Dark Poetry):\n"
    msg += f"{social_data.get('caption_b', 'N/A')}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n📌 PİNTEREST:\n"
    msg += f"{social_data.get('pinterest', pin_text)}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n🛒 ETSY LİSTİNG OPTİMİZASYONU:\n"
    msg += f"Başlık: {social_data.get('etsy_title', 'N/A')}\n"
    msg += f"Etiketler: {', '.join(social_data.get('etsy_tags', []))}\n"
    msg += f"Açıklama: {social_data.get('etsy_description', 'N/A')}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🔗 ÜRÜN LİNKİ (Story için kopyala):\n{product_url}\n\n"
    msg += "⏰ ÖNERİLEN PAYLAŞIM SAATİ:\nBugün 21:00-22:00 EST (TR: 04:00-05:00)\n\n━━━━━━━━━━━━━━━━━━━━━━"

    keyboard = [
        [InlineKeyboardButton("✅ Yayınla (Caption A)", callback_data=f"approveA_{index}"),
         InlineKeyboardButton("✅ Yayınla (Caption B)", callback_data=f"approveB_{index}")],
        [InlineKeyboardButton("🔄 Yeniden Üret", callback_data=f"recreate_{index}"),
         InlineKeyboardButton("❌ Atla", callback_data=f"skip_{index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if vid_file and os.path.exists(vid_file):
            with open(vid_file, 'rb') as video:
                await context.bot.send_video(chat_id=TELEGRAM_GROUP_ID, video=video, read_timeout=120, write_timeout=120, connect_timeout=120)
        elif img_file and os.path.exists(img_file):
            with open(img_file, 'rb') as image:
                await context.bot.send_photo(chat_id=TELEGRAM_GROUP_ID, photo=image, read_timeout=120, write_timeout=120, connect_timeout=120)
                
        await context.bot.send_message(
            chat_id=TELEGRAM_GROUP_ID, 
            text=msg, 
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            read_timeout=120,
            write_timeout=120,
            connect_timeout=120
        )
    except Exception as e:
        print(f"Failed to send to Telegram: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action, index_str = query.data.split('_')
    index = int(index_str)
    
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        
    if index >= len(reader):
        await query.edit_message_text("Hata: Post bulunamadı.")
        return
        
    row = reader[index]
    if row[5] in ["PUBLISHED", "SKIPPED"]:
        await query.edit_message_text("Bu gönderi zaten işlenmiş.")
        return
        
    vid_file = f"reels_output/{row[3]}"
    img_file = f"bulk_images/{row[2]}"
    product_url = row[4]
    
    prod_id = row[2].replace("post_", "").replace(".jpg", "")
    
    try:
        social_data = json.loads(row[0])
        caption = social_data.get("caption_a", "Deathlipse 🖤")
    except:
        caption = row[0]
        
    if action == "skip":
        update_status(index, "SKIPPED", prod_id)
        await query.edit_message_text("❌ Gönderi atlandı (Skipped).")
        
    elif action == "recreate":
        # Video generator çağırarak aynı resimle tekrar video üretiriz (farklı style ve müzik denk gelir)
        await query.edit_message_text("🔄 Video yeniden üretiliyor...")
        try:
            ptype = "hoodie" if "hoodie" in vid_file else "tshirt"
            # Hook text json içindeyse alalım
            hook = social_data.get("hook", "") if isinstance(social_data, dict) else ""
            video_generator.generate_tiktok_video(img_file, vid_file, hook_text=hook, product_type=ptype)
            await query.edit_message_text("✅ Video yeniden üretildi. Yeniden onay ekranı getiriliyor...")
            # Yeni onay ekranını yolla
            await check_for_posts(context)
        except Exception as e:
            await query.edit_message_text(f"❌ Yeniden üretim başarısız oldu: {e}")
            
    elif action in ["approveA", "approveB"]:
        await query.edit_message_text("⏳ İşleniyor... Lütfen bekleyin...")
        
        try:
            if action == "approveB":
                caption = social_data.get("caption_b", caption)
            else:
                caption = social_data.get("caption_a", caption)
        except Exception:
            pass
        
        # Social Media Posting
        tiktok_config = [{"platform": "tiktok", "accountId": ZERNIO_TIKTOK_ACCOUNT_ID}]
        pinterest_config = [{"platform": "pinterest", "accountId": ZERNIO_PINTEREST_ACCOUNT_ID}]
        
        t_res = post_to_zernio(caption, vid_file, tiktok_config, "video")
        
        # Fallback to standard caption if Pinterest text is missing
        p_caption = row[1] if len(row) > 1 and row[1].strip() else caption
        p_res = post_to_zernio(p_caption, img_file, pinterest_config, "image")
        
        # Meta Reels
        meta_reels_res = await post_video_to_meta_graph_reels(vid_file, caption)
        
        # Story
        story_res = False
        try:
            ptype = "hoodie" if "hoodie" in vid_file else "tshirt"
            story_img = video_generator.generate_story_image(img_file, ptype)
            # Hardcoded ETSY link for story as requested by the user
            story_res = post_to_meta_graph(story_img, "https://deathlipse.etsy.com")
            if os.path.exists(story_img):
                os.remove(story_img)
        except Exception as e:
            print(f"Story generation failed: {e}")
            
        update_status(index, "PUBLISHED", prod_id)
        
        res_msg = "📊 YAYIN SONUÇLARI:\n"
        res_msg += f"✅ TikTok Reel: {'Yayınlandı' if t_res else 'Başarısız'}\n"
        res_msg += f"✅ Instagram Reel: {'Yayınlandı' if i_res else 'Başarısız'}\n"
        res_msg += f"✅ Instagram Story: {'Yayınlandı' if story_res else 'Başarısız'}\n\n"
        res_msg += f"🔗 Etsy: {product_url}"
        
        await query.edit_message_text(res_msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Deathlipse Otomasyon Hub'ı Aktif! Günde 1 kez onay postu atacak.")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Manuel test tetiklendi, sıradaki gönderi aranıyor...")
    await check_for_posts(context)

def main():
    print("Starting Deathlipse Telegram Bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    job_queue = application.job_queue
    # TR Saati (UTC+3) -> 09:00 TR == 06:00 UTC
    target_time = dt_time(hour=6, minute=0, tzinfo=timezone.utc)
    
    # Send once immediately for testing, then schedule daily
    job_queue.run_once(check_for_posts, 5)
    job_queue.run_daily(check_for_posts, target_time)
    
    # Check token expiry daily
    job_queue.run_daily(check_token_expiry, target_time)
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
