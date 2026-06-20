"""
Telegram onay ve ürün seçici sistemi.
/pick komutuyla ürün listesi → seçim → önizleme → zamanlı yayın.
"""
import os
import csv
import json
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.config import CSV_FILE, POSTED_JSON, TELEGRAM_GROUP_ID
from content import video_generator
from bot.publisher import schedule_post, update_post_status, get_next_us_peak_time

PRODUCTS_PER_PAGE = 8

def get_all_pending_posts():
    """Tüm PENDING durumundaki gönderileri döndürür."""
    if not os.path.isfile(CSV_FILE):
        return []
    
    pending = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    for i in range(1, len(reader)):
        row = reader[i]
        while len(row) < 6:
            row.append("PENDING")
        if row[5] == "PENDING":
            # Ürün adını çıkar
            try:
                social_data = json.loads(row[0])
                title = social_data.get("etsy_title", "").split("|")[0].strip()
                if not title:
                    title = row[2].split("/")[-2].replace("_", " ") if "/" in row[2] else f"Ürün #{i}"
            except:
                title = row[2].split("/")[-2].replace("_", " ") if "/" in row[2] else f"Ürün #{i}"
            
            pending.append({
                "index": i,
                "title": title[:50],  # Telegram buton limiti
                "row": row
            })
    
    return pending

def get_caption_data(row):
    """Bir ürünün caption.json veya CSV verilerinden caption bilgisini okur."""
    caption_data = {}
    
    # Önce caption.json'dan oku
    if "/" in row[2]:
        media_dir = os.path.dirname(row[2])
        caption_json_path = os.path.join(media_dir, "caption.json")
        if os.path.exists(caption_json_path):
            try:
                with open(caption_json_path, "r", encoding="utf-8") as f:
                    caption_data = json.load(f)
            except Exception as e:
                print(f"caption.json read error: {e}")
    
    # caption.json yoksa CSV'deki JSON'ı kullan
    if not caption_data:
        try:
            caption_data = json.loads(row[0])
        except:
            caption_data = {"caption_a": row[0]}
    
    return caption_data

async def send_product_list(context_or_update, chat_id, page=0):
    """Bekleyen ürünlerin listesini sayfalı butonlarla gönderir."""
    pending = get_all_pending_posts()
    
    if not pending:
        if hasattr(context_or_update, 'bot'):
            await context_or_update.bot.send_message(
                chat_id=chat_id,
                text="✅ Tebrikler! Bekleyen gönderi kalmadı."
            )
        return
    
    total_pages = math.ceil(len(pending) / PRODUCTS_PER_PAGE)
    page = min(page, total_pages - 1)
    
    start = page * PRODUCTS_PER_PAGE
    end = min(start + PRODUCTS_PER_PAGE, len(pending))
    page_items = pending[start:end]
    
    msg = f"📋 BEKLEYEN ÜRÜNLER ({len(pending)} adet)\n"
    msg += f"Sayfa {page + 1}/{total_pages}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "Paylaşmak istediğin ürünü seç:\n"
    
    keyboard = []
    for item in page_items:
        # Ürün tipini belirle (emoji için)
        title_lower = item["title"].lower()
        if "hoodie" in title_lower:
            emoji = "🧥"
        elif "t-shirt" in title_lower or "tee" in title_lower or "tshirt" in title_lower:
            emoji = "👕"
        else:
            emoji = "🎽"
        
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} {item['title']}", 
                callback_data=f"pick_{item['index']}"
            )
        ])
    
    # Sayfalama butonları
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Önceki", callback_data=f"page_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Sonraki ➡️", callback_data=f"page_{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    bot = context_or_update.bot if hasattr(context_or_update, 'bot') else context_or_update
    await bot.send_message(
        chat_id=chat_id,
        text=msg,
        reply_markup=reply_markup
    )

async def send_product_preview(bot, chat_id, csv_index):
    """Seçilen ürünün video + caption önizlemesini gönderir."""
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    if csv_index >= len(reader):
        await bot.send_message(chat_id=chat_id, text="❌ Ürün bulunamadı.")
        return
    
    row = reader[csv_index]
    caption_data = get_caption_data(row)
    
    vid_file = row[3] if "/" in row[3] else f"reels_output/{row[3]}"
    img_file = row[2] if "/" in row[2] else f"bulk_images/{row[2]}"
    product_url = row[4] if len(row) > 4 else ""
    
    # Peak zamanı hesapla
    peak = get_next_us_peak_time()
    from datetime import timedelta
    est_str = (peak - timedelta(hours=5)).strftime("%d/%m %H:%M EST")
    tr_str = (peak + timedelta(hours=3)).strftime("%d/%m %H:%M TR")
    
    # Önizleme mesajı
    msg = "🎬 ÜRÜN ÖNİZLEME\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📝 CAPTION A (Agresif):\n{caption_data.get('caption_a', 'N/A')}\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📝 CAPTION B (Dark Poetry):\n{caption_data.get('caption_b', 'N/A')}\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📌 PINTEREST:\n{caption_data.get('pinterest', 'N/A')}\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🛒 ETSY:\nBaşlık: {caption_data.get('etsy_title', 'N/A')}\n"
    msg += f"Etiketler: {', '.join(caption_data.get('etsy_tags', []))}\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🔗 ÜRÜN LİNKİ:\n{product_url}\n\n"
    msg += f"⏰ PLANLANACAK SAAT:\n{est_str} ({tr_str})\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━"
    
    keyboard = [
        [InlineKeyboardButton("✅ Yayınla (Caption A)", callback_data=f"scheduleA_{csv_index}"),
         InlineKeyboardButton("✅ Yayınla (Caption B)", callback_data=f"scheduleB_{csv_index}")],
        [InlineKeyboardButton("🔄 Yeniden Üret", callback_data=f"recreate_{csv_index}"),
         InlineKeyboardButton("❌ Atla", callback_data=f"skip_{csv_index}")],
        [InlineKeyboardButton("🔙 Listeye Dön", callback_data="page_0")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Videoyu gönder
    try:
        if vid_file and os.path.exists(vid_file):
            with open(vid_file, 'rb') as video:
                await bot.send_video(
                    chat_id=chat_id, video=video,
                    read_timeout=120, write_timeout=120, connect_timeout=120
                )
        elif img_file and os.path.exists(img_file):
            with open(img_file, 'rb') as image:
                await bot.send_photo(
                    chat_id=chat_id, photo=image,
                    read_timeout=120, write_timeout=120, connect_timeout=120
                )
    except Exception as e:
        print(f"Failed to send media: {e}")
    
    # Caption + butonları gönder
    # Telegram mesaj limiti 4096 karakter
    if len(msg) > 4096:
        for i in range(0, len(msg), 4096):
            chunk = msg[i:i+4096]
            if i + 4096 >= len(msg):
                await bot.send_message(
                    chat_id=chat_id, text=chunk,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                    read_timeout=120, write_timeout=120, connect_timeout=120
                )
            else:
                await bot.send_message(
                    chat_id=chat_id, text=chunk,
                    disable_web_page_preview=True,
                    read_timeout=120, write_timeout=120, connect_timeout=120
                )
    else:
        await bot.send_message(
            chat_id=chat_id, text=msg,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            read_timeout=120, write_timeout=120, connect_timeout=120
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm buton tıklamalarını yönetir."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    chat_id = query.message.chat_id
    
    # Sayfalama
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await send_product_list(context, chat_id, page)
        return
    
    # Ürün seçimi → Önizleme
    if data.startswith("pick_"):
        csv_index = int(data.split("_")[1])
        await send_product_preview(context.bot, chat_id, csv_index)
        return
    
    # Zamanlı yayın
    if data.startswith("scheduleA_") or data.startswith("scheduleB_"):
        action, index_str = data.split("_", 1)
        csv_index = int(index_str)
        caption_choice = "b" if action == "scheduleB" else "a"
        
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
        
        if csv_index >= len(reader):
            await query.edit_message_text("❌ Gönderi bulunamadı.")
            return
        
        row = reader[csv_index]
        if len(row) >= 6 and row[5] in ["PUBLISHED", "SKIPPED", "SCHEDULED"]:
            await query.edit_message_text("Bu gönderi zaten işlenmiş veya planlanmış.")
            return
        
        time_info = schedule_post(csv_index, caption_choice)
        
        await query.edit_message_text(
            f"✅ Gönderi planlandı!\n\n"
            f"⏰ Yayın Zamanı: {time_info['est']} ({time_info['tr']})\n\n"
            f"Bot bu saatte otomatik olarak tüm platformlara yayınlayacak.\n"
            f"Başka bir ürün seçmek için /pick yazın."
        )
        return
    
    # Atla
    if data.startswith("skip_"):
        csv_index = int(data.split("_")[1])
        
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
        
        row = reader[csv_index]
        try:
            social_data = json.loads(row[0])
            prod_id = social_data.get("product_id")
        except:
            prod_id = None
        
        if not prod_id:
            prod_id = row[2].split("/")[-1].replace("post_", "").replace(".jpg", "").replace(".png", "")
        
        update_post_status(csv_index, "SKIPPED", prod_id)
        await query.edit_message_text("❌ Gönderi atlandı. Başka bir ürün seçmek için /pick yazın.")
        return
    
    # Yeniden üret
    if data.startswith("recreate_"):
        csv_index = int(data.split("_")[1])
        await query.edit_message_text("🔄 Video yeniden üretiliyor...")
        
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
        
        row = reader[csv_index]
        vid_file = row[3] if "/" in row[3] else f"reels_output/{row[3]}"
        img_file = row[2] if "/" in row[2] else f"bulk_images/{row[2]}"
        
        try:
            social_data = json.loads(row[0])
        except:
            social_data = {}
        
        caption_data = get_caption_data(row)
        
        try:
            ptype = "t-shirt"
            for t in ["hoodie", "sweatshirt", "tank_top", "tote_bag", "poster", "t-shirt", "tshirt"]:
                if t in vid_file.lower():
                    ptype = "t-shirt" if t == "tshirt" else t
                    break
            hook = caption_data.get("hook", social_data.get("hook", ""))
            video_generator.generate_tiktok_video(img_file, vid_file, hook_text=hook, product_type=ptype)
            await query.edit_message_text("✅ Video yeniden üretildi! Önizleme getiriliyor...")
            await send_product_preview(context.bot, chat_id, csv_index)
        except Exception as e:
            await query.edit_message_text(f"❌ Yeniden üretim başarısız: {e}")
        return

# Eski uyumluluk — artık kullanılmıyor ama import hatası olmasın diye bırakıyoruz
def get_next_pending_post():
    pending = get_all_pending_posts()
    if pending:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
        return reader[pending[0]["index"]], pending[0]["index"]
    return None, -1

async def check_for_posts(context: ContextTypes.DEFAULT_TYPE):
    """Eski fonksiyon — artık /pick kullanılıyor ama uyumluluk için bırakıyoruz."""
    await send_product_list(context, TELEGRAM_GROUP_ID, page=0)
