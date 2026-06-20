"""
Zamanlı yayın motoru.
SCHEDULED durumundaki gönderileri ABD peak saatlerinde otomatik yayınlar.
"""
import os
import csv
import json
from datetime import datetime, timezone, timedelta
from telegram.ext import ContextTypes
from core.config import (
    CSV_FILE, POSTED_JSON, TELEGRAM_GROUP_ID,
    ZERNIO_TIKTOK_ACCOUNT_ID, ZERNIO_PINTEREST_ACCOUNT_ID
)
from publishers import instagram, tiktok, pinterest, threads
from publishers.youtube import upload_video_to_shorts
from content import video_generator

# ABD EST (UTC-5) — Peak saat: 21:00 EST = 02:00 UTC (ertesi gün)
US_PEAK_HOUR_UTC = 2  # 21:00 EST = 02:00 UTC
US_PEAK_MINUTE = 0

def get_next_us_peak_time():
    """Bir sonraki ABD peak yayın zamanını hesaplar (21:00 EST / 02:00 UTC)."""
    now = datetime.now(timezone.utc)
    
    # Bugünün peak saati
    today_peak = now.replace(hour=US_PEAK_HOUR_UTC, minute=US_PEAK_MINUTE, second=0, microsecond=0)
    
    # Eğer peak saati geçtiyse yarına planla
    if now >= today_peak:
        today_peak += timedelta(days=1)
    
    return today_peak

def schedule_post(csv_index, caption_choice="a"):
    """Bir gönderiyi SCHEDULED durumuna alır ve peak zamanını yazar."""
    peak_time = get_next_us_peak_time()
    
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    row = reader[csv_index]
    while len(row) < 8:
        row.append("")
    
    row[5] = "SCHEDULED"
    row[6] = peak_time.isoformat()  # Planlanan zaman
    row[7] = caption_choice  # Hangi caption seçildi (a veya b)
    
    reader[csv_index] = row
    
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(reader)
    
    # EST saatini hesapla (gösterim için)
    est_time = peak_time - timedelta(hours=5)
    tr_time = peak_time + timedelta(hours=3)
    
    return {
        "est": est_time.strftime("%H:%M EST"),
        "tr": tr_time.strftime("%H:%M TR"),
        "utc": peak_time.isoformat()
    }

def get_scheduled_posts():
    """Zamanı gelmiş SCHEDULED gönderileri döndürür."""
    if not os.path.isfile(CSV_FILE):
        return []
    
    now = datetime.now(timezone.utc)
    ready = []
    
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    for i in range(1, len(reader)):
        row = reader[i]
        if len(row) >= 7 and row[5] == "SCHEDULED" and row[6]:
            try:
                scheduled_time = datetime.fromisoformat(row[6])
                if now >= scheduled_time:
                    caption_choice = row[7] if len(row) > 7 else "a"
                    ready.append((row, i, caption_choice))
            except (ValueError, IndexError):
                continue
    
    return ready

def update_post_status(index, status, product_id=""):
    """CSV ve JSON'daki durumu günceller."""
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    while len(reader[index]) < 8:
        reader[index].append("")
    reader[index][5] = status
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(reader)
    
    if product_id and os.path.exists(POSTED_JSON):
        try:
            with open(POSTED_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            if product_id in data:
                data[product_id]["status"] = status
                with open(POSTED_JSON, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to update posted_products.json: {e}")

async def publish_post(row, caption_choice="a"):
    """Tek bir gönderiyi tüm platformlara yayınlar."""
    try:
        social_data = json.loads(row[0])
    except:
        social_data = {"caption_a": row[0]}
    
    vid_file = row[3] if "/" in row[3] else f"reels_output/{row[3]}"
    img_file = row[2] if "/" in row[2] else f"bulk_images/{row[2]}"
    product_url = row[4]
    
    # Caption.json dosyasından oku (varsa)
    caption_json_path = None
    if "/" in row[2]:
        media_dir = os.path.dirname(row[2])
        caption_json_path = os.path.join(media_dir, "caption.json")
    
    if caption_json_path and os.path.exists(caption_json_path):
        try:
            with open(caption_json_path, "r", encoding="utf-8") as f:
                caption_data = json.load(f)
            if caption_choice == "b":
                caption = caption_data.get("caption_b", social_data.get("caption_b", "Deathlipse 🖤"))
            else:
                caption = caption_data.get("caption_a", social_data.get("caption_a", "Deathlipse 🖤"))
            social_data.update(caption_data)
        except Exception as e:
            print(f"Caption.json read error: {e}")
            caption = social_data.get(f"caption_{caption_choice}", social_data.get("caption_a", "Deathlipse 🖤"))
    else:
        caption = social_data.get(f"caption_{caption_choice}", social_data.get("caption_a", "Deathlipse 🖤"))
    
    prod_id = social_data.get("product_id")
    if not prod_id:
        prod_id = row[2].split("/")[-1].replace("post_", "").replace(".png", "").replace(".jpg", "")
    
    results = {}
    
    # TikTok
    try:
        results["tiktok"] = tiktok.post(caption, vid_file, "video")
    except Exception as e:
        print(f"TikTok fail: {e}")
        results["tiktok"] = False
    
    # Pinterest
    p_caption = row[1] if len(row) > 1 and row[1].strip() else caption
    try:
        results["pinterest"] = pinterest.post(p_caption, img_file, "image")
    except Exception as e:
        print(f"Pinterest fail: {e}")
        results["pinterest"] = False
    
    # Instagram Reels
    try:
        results["ig_reels"] = await instagram.post_reels(vid_file, caption)
    except Exception as e:
        print(f"IG Reels fail: {e}")
        results["ig_reels"] = False
    
    # YouTube Shorts
    try:
        yt_title = social_data.get("etsy_title", "Deathlipse 🖤")
        yt_desc = caption
        yt_tags_raw = social_data.get("etsy_tags", "metal,goth,streetwear")
        if isinstance(yt_tags_raw, str):
            yt_tags = [t.strip() for t in yt_tags_raw.split(",") if t.strip()]
        else:
            yt_tags = yt_tags_raw
        results["youtube"] = upload_video_to_shorts(vid_file, yt_title, yt_desc, yt_tags)
    except Exception as e:
        print(f"YouTube fail: {e}")
        results["youtube"] = False
    
    # Threads
    try:
        results["threads"] = threads.post(img_file, caption, product_url)
    except Exception as e:
        print(f"Threads fail: {e}")
        results["threads"] = False
    
    # Instagram Story
    try:
        ptype = "t-shirt"
        for t in ["hoodie", "sweatshirt", "tank_top", "tote_bag", "poster", "t-shirt", "tshirt"]:
            if t in vid_file.lower():
                ptype = "t-shirt" if t == "tshirt" else t
                break
        story_img = video_generator.generate_story_image(img_file, ptype)
        results["ig_story"] = instagram.post_story(story_img, "https://deathlipse.etsy.com")
        if os.path.exists(story_img):
            os.remove(story_img)
    except Exception as e:
        print(f"Story fail: {e}")
        results["ig_story"] = False
    
    return results, prod_id

async def scheduled_publish_job(context: ContextTypes.DEFAULT_TYPE):
    """Her 15 dakikada çalışır, zamanı gelmiş gönderileri yayınlar."""
    ready_posts = get_scheduled_posts()
    
    if not ready_posts:
        return
    
    for row, index, caption_choice in ready_posts:
        try:
            print(f"[SCHEDULER] Publishing scheduled post at index {index}...")
            results, prod_id = await publish_post(row, caption_choice)
            update_post_status(index, "PUBLISHED", prod_id)
            
            # Telegram'a sonuç bildir
            product_url = row[4] if len(row) > 4 else ""
            res_msg = "📊 ZAMANLI YAYIN SONUÇLARI:\n"
            res_msg += f"{'✅' if results.get('tiktok') else '❌'} TikTok Reel\n"
            res_msg += f"{'✅' if results.get('pinterest') else '❌'} Pinterest\n"
            res_msg += f"{'✅' if results.get('ig_reels') else '❌'} Instagram Reel\n"
            res_msg += f"{'✅' if results.get('ig_story') else '❌'} Instagram Story\n"
            res_msg += f"{'✅' if results.get('threads') else '❌'} Threads\n"
            res_msg += f"{'✅' if results.get('youtube') else '❌'} YouTube Shorts\n\n"
            res_msg += f"🔗 Etsy: {product_url}"
            
            await context.bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=res_msg,
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"[SCHEDULER] Failed to publish post at index {index}: {e}")
            try:
                await context.bot.send_message(
                    chat_id=TELEGRAM_GROUP_ID,
                    text=f"❌ Zamanlı yayın başarısız (index {index}): {e}"
                )
            except:
                pass
