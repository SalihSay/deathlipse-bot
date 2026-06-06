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
import youtube_uploader

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

def upload_to_tmpfiles(file_path):
    print(f"Uploading to tmpfiles.org: {file_path}")
    url = "https://tmpfiles.org/api/v1/upload"
    with open(file_path, "rb") as f:
        files = {"file": f}
        try:
            resp = requests.post(url, files=files)
            data = resp.json()
            if data.get("status") == "success":
                file_url = data["data"]["url"]
                direct_url = file_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                return direct_url
            print(f"Upload failed. Response: {data}")
        except Exception as e:
            print("Upload exception:", e)
    return None

def post_to_meta_graph(story_image_path, product_url):
    if not META_ACCESS_TOKEN or not META_IG_USER_ID:
        print("[!] Meta API tokens missing.")
        return False
        
    image_url = upload_to_tmpfiles(story_image_path)
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
        
    video_url = upload_to_tmpfiles(video_path)
    if not video_url:
        return False
        
    print("Posting Reels to Meta Graph API...")
    container_url = f"https://graph.facebook.com/v19.0/{META_IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true",
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
        for _ in range(24):  # Max 240 seconds
            status_resp = requests.get(status_url)
            status_data = status_resp.json()
            if status_data.get("status_code") == "FINISHED":
                break
            elif status_data.get("status_code") == "ERROR":
                print(f"Reels processing error: {status_data}")
                return False
            await asyncio.sleep(10)
            
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

def post_to_threads(image_path, caption, product_url):
    if not META_ACCESS_TOKEN or not META_IG_USER_ID:
        print("[!] Meta API tokens missing for Threads.")
        return False
        
    image_url = upload_to_tmpfiles(image_path)
    if not image_url:
        return False
        
    print("Posting to Threads API...")
    container_url = f"https://graph.threads.net/v1.0/{META_IG_USER_ID}/threads"
    
    thread_text = f"{caption}\n\nShop now: {product_url}"
    payload = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": thread_text,
        "access_token": META_ACCESS_TOKEN
    }
    
    try:
        resp = requests.post(container_url, data=payload)
        data = resp.json()
        if "id" not in data:
            print(f"Threads Container failed: {data}")
            return False
            
        creation_id = data["id"]
        # Step 2: Publish
        publish_url = f"https://graph.threads.net/v1.0/{META_IG_USER_ID}/threads_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": META_ACCESS_TOKEN
        }
        pub_resp = requests.post(publish_url, data=publish_payload)
        pub_data = pub_resp.json()
        if "id" in pub_data:
            print(f"Threads Published! ID: {pub_data['id']}")
            return True
        else:
            print(f"Threads Publish failed: {pub_data}")
            return False
            
    except Exception as e:
        print("Threads API exception:", e)
        return False

def post_to_zernio(text, media_path, platforms_config, media_type="video"):
    if not ZERNIO_API_KEY:
        return False
        
    media_url = upload_to_tmpfiles(media_path)
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
            ptype = "t-shirt"
            for t in ["hoodie", "sweatshirt", "tank_top", "tote_bag", "poster", "t-shirt", "tshirt"]:
                if t in vid_file.lower():
                    ptype = "t-shirt" if t == "tshirt" else t
                    break
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
        
        try:
            t_res = post_to_zernio(caption, vid_file, tiktok_config, "video")
        except Exception as e:
            print(f"Zernio TikTok fail: {e}")
            t_res = False
        
        # Fallback to standard caption if Pinterest text is missing
        p_caption = row[1] if len(row) > 1 and row[1].strip() else caption
        try:
            p_res = post_to_zernio(p_caption, img_file, pinterest_config, "image")
        except Exception as e:
            print(f"Zernio Pinterest fail: {e}")
            p_res = False
        
        # Meta Reels
        meta_reels_res = False
        try:
            meta_reels_res = await post_video_to_meta_graph_reels(vid_file, caption)
        except Exception as e:
            print(f"Meta Reels fail: {e}")
        
        # YouTube Shorts
        yt_res = False
        try:
            yt_title = social_data.get("etsy_title", "Deathlipse 🖤") if isinstance(social_data, dict) else "Deathlipse 🖤"
            yt_desc = caption
            yt_tags_raw = social_data.get("etsy_tags", "metal,goth,streetwear") if isinstance(social_data, dict) else "metal,goth"
            if isinstance(yt_tags_raw, str):
                yt_tags = [t.strip() for t in yt_tags_raw.split(",") if t.strip()]
            else:
                yt_tags = yt_tags_raw
            
            print("Uploading to YouTube Shorts...")
            yt_res = youtube_uploader.upload_video_to_shorts(vid_file, yt_title, yt_desc, yt_tags)
        except Exception as e:
            print(f"YouTube Shorts fail: {e}")
        
        # Threads
        threads_res = False
        try:
            threads_res = post_to_threads(img_file, caption, product_url)
        except Exception as e:
            print(f"Threads fail: {e}")
        
        # Story
        story_res = False
        try:
            ptype = "t-shirt"
            for t in ["hoodie", "sweatshirt", "tank_top", "tote_bag", "poster", "t-shirt", "tshirt"]:
                if t in vid_file.lower():
                    ptype = "t-shirt" if t == "tshirt" else t
                    break
            story_img = video_generator.generate_story_image(img_file, ptype)
            # Hardcoded ETSY link for story as requested by the user
            story_res = post_to_meta_graph(story_img, "https://deathlipse.etsy.com")
            if os.path.exists(story_img):
                os.remove(story_img)
        except Exception as e:
            print(f"Story generation failed: {e}")
            
        update_status(index, "PUBLISHED", prod_id)
        
        res_msg = "📊 YAYIN SONUÇLARI:\n"
        res_msg += f"{'✅' if t_res else '❌'} TikTok Reel: {'Yayınlandı' if t_res else 'Başarısız'}\n"
        res_msg += f"{'✅' if p_res else '❌'} Pinterest: {'Yayınlandı' if p_res else 'Başarısız'}\n"
        res_msg += f"{'✅' if meta_reels_res else '❌'} Instagram Reel: {'Yayınlandı' if meta_reels_res else 'Başarısız'}\n"
        res_msg += f"{'✅' if story_res else '❌'} Instagram Story: {'Yayınlandı' if story_res else 'Başarısız'}\n"
        res_msg += f"{'✅' if threads_res else '❌'} Threads: {'Yayınlandı' if threads_res else 'Başarısız'}\n"
        res_msg += f"{'✅' if yt_res else '❌'} YouTube Shorts: {'Yayınlandı' if yt_res else 'Başarısız'}\n\n"
        res_msg += f"🔗 Etsy: {product_url}"
        
        await query.edit_message_text(res_msg)

async def run_generator_job(context: ContextTypes.DEFAULT_TYPE):
    print("Running daily bulk content generator...")
    proc = await asyncio.create_subprocess_exec(
        "python", "bulk_content_generator.py", "--batch", "1",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    print(f"Generator finished with code {proc.returncode}")
    await check_for_posts(context)

async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    row, index = get_next_pending_post()
    if not row:
        return
        
    msg = "⚠️ *Önemli Hatırlatma!*\n\nBugünkü gönderiyi hala onaylamadınız. Gönderinin zamanında yayınlanması için yukarıdaki mesajdan onaylamayı unutmayın!"
    try:
        await context.bot.send_message(
            chat_id=TELEGRAM_GROUP_ID, 
            text=msg, 
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Failed to send reminder: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Deathlipse Otomasyon Hub'ı Aktif! Her gün yeni post üretilecek ve onay bekleyecek.\nKomutlar:\n/test - Sıradaki bekleyen gönderiyi getirir\n/skip_current - Bekleyen gönderiyi atlar\n/status - Kuyruk durumunu gösterir")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Manuel test tetiklendi, sıradaki gönderi aranıyor...")
    await check_for_posts(context)

async def skip_current_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    row, index = get_next_pending_post()
    if not row:
        await update.message.reply_text("Şu anda bekleyen (PENDING) hiçbir gönderi yok.")
        return
    prod_id = row[2].replace("post_", "").replace(".jpg", "").replace(".png", "")
    update_status(index, "SKIPPED", prod_id)
    await update.message.reply_text(f"✅ {prod_id} ID'li gönderi başarıyla atlandı! Sıradaki ürünü görmek için /test yazabilirsiniz.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.isfile(CSV_FILE):
        await update.message.reply_text("CSV dosyası bulunamadı.")
        return
    
    pending_count = 0
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        for i in range(1, len(reader)):
            row = reader[i]
            if len(row) >= 6 and row[5] == "PENDING":
                pending_count += 1
                
    await update.message.reply_text(f"📊 Kuyruk Durumu:\nŞu anda onay bekleyen {pending_count} adet gönderi var.")

def main():
    print("Starting Deathlipse Telegram Bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("skip_current", skip_current_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    job_queue = application.job_queue
    
    # 07:00 UTC = 10:00 TR Time -> Her gün saat 10:00'da post üretimi başlar
    target_time_gen = dt_time(hour=7, minute=0, tzinfo=timezone.utc)
    job_queue.run_daily(run_generator_job, target_time_gen)
    
    # Hatırlatıcılar (TR: 12:00, 15:00, 18:00, 21:00) (UTC: 09:00, 12:00, 15:00, 18:00)
    reminders_utc = [
        dt_time(hour=9, minute=0, tzinfo=timezone.utc),
        dt_time(hour=12, minute=0, tzinfo=timezone.utc),
        dt_time(hour=15, minute=0, tzinfo=timezone.utc),
        dt_time(hour=18, minute=0, tzinfo=timezone.utc),
    ]
    for r_time in reminders_utc:
        job_queue.run_daily(reminder_job, r_time)
    
    # Check token expiry daily at 06:00 UTC
    job_queue.run_daily(check_token_expiry, dt_time(hour=6, minute=0, tzinfo=timezone.utc))
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
