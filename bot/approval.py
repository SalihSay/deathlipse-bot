import os
import csv
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.config import (
    CSV_FILE, POSTED_JSON, TELEGRAM_GROUP_ID,
    ZERNIO_TIKTOK_ACCOUNT_ID, ZERNIO_PINTEREST_ACCOUNT_ID
)
from publishers import instagram, tiktok, pinterest, threads
from publishers.youtube import upload_video_to_shorts
from content import video_generator

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
        await query.edit_message_text("🔄 Video yeniden üretiliyor...")
        try:
            ptype = "t-shirt"
            for t in ["hoodie", "sweatshirt", "tank_top", "tote_bag", "poster", "t-shirt", "tshirt"]:
                if t in vid_file.lower():
                    ptype = "t-shirt" if t == "tshirt" else t
                    break
            hook = social_data.get("hook", "") if isinstance(social_data, dict) else ""
            video_generator.generate_tiktok_video(img_file, vid_file, hook_text=hook, product_type=ptype)
            await query.edit_message_text("✅ Video yeniden üretildi. Yeniden onay ekranı getiriliyor...")
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
        
        try:
            t_res = tiktok.post(caption, vid_file, "video")
        except Exception as e:
            print(f"Zernio TikTok fail: {e}")
            t_res = False
        
        p_caption = row[1] if len(row) > 1 and row[1].strip() else caption
        try:
            p_res = pinterest.post(p_caption, img_file, "image")
        except Exception as e:
            print(f"Zernio Pinterest fail: {e}")
            p_res = False
        
        meta_reels_res = False
        try:
            meta_reels_res = await instagram.post_reels(vid_file, caption)
        except Exception as e:
            print(f"Meta Reels fail: {e}")
        
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
            yt_res = upload_video_to_shorts(vid_file, yt_title, yt_desc, yt_tags)
        except Exception as e:
            print(f"YouTube Shorts fail: {e}")
        
        threads_res = False
        try:
            threads_res = threads.post(img_file, caption, product_url)
        except Exception as e:
            print(f"Threads fail: {e}")
        
        story_res = False
        try:
            ptype = "t-shirt"
            for t in ["hoodie", "sweatshirt", "tank_top", "tote_bag", "poster", "t-shirt", "tshirt"]:
                if t in vid_file.lower():
                    ptype = "t-shirt" if t == "tshirt" else t
                    break
            story_img = video_generator.generate_story_image(img_file, ptype)
            story_res = instagram.post_story(story_img, "https://deathlipse.etsy.com")
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
