import os
import csv
from telegram import Update
from telegram.ext import ContextTypes
from core.config import CSV_FILE, TELEGRAM_GROUP_ID
from bot.approval import send_product_list, get_all_pending_posts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🖤 Deathlipse Otomasyon Hub'ı Aktif!\n\n"
        "Komutlar:\n"
        "/pick — Ürün seç ve paylaş\n"
        "/status — Kuyruk durumunu göster\n"
        "/scheduled — Planlanmış gönderileri göster\n"
    )

async def pick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bekleyen ürünlerin listesini getirir — kullanıcı seçer."""
    await update.message.reply_text("📋 Bekleyen ürünler yükleniyor...")
    await send_product_list(context, update.effective_chat.id, page=0)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.isfile(CSV_FILE):
        await update.message.reply_text("CSV dosyası bulunamadı.")
        return
    
    pending_count = 0
    scheduled_count = 0
    published_count = 0
    skipped_count = 0
    
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        for i in range(1, len(reader)):
            row = reader[i]
            status = row[5] if len(row) >= 6 else "PENDING"
            if status == "PENDING":
                pending_count += 1
            elif status == "SCHEDULED":
                scheduled_count += 1
            elif status == "PUBLISHED":
                published_count += 1
            elif status == "SKIPPED":
                skipped_count += 1
    
    msg = "📊 KUYRUK DURUMU:\n\n"
    msg += f"⏳ Bekleyen: {pending_count}\n"
    msg += f"📅 Planlanmış: {scheduled_count}\n"
    msg += f"✅ Yayınlanmış: {published_count}\n"
    msg += f"❌ Atlanan: {skipped_count}\n\n"
    msg += f"📦 Toplam: {pending_count + scheduled_count + published_count + skipped_count}\n\n"
    msg += "Ürün seçmek için /pick yazın."
    
    await update.message.reply_text(msg)

async def scheduled_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Planlanmış gönderileri listeler."""
    if not os.path.isfile(CSV_FILE):
        await update.message.reply_text("CSV dosyası bulunamadı.")
        return
    
    scheduled = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        for i in range(1, len(reader)):
            row = reader[i]
            if len(row) >= 7 and row[5] == "SCHEDULED":
                try:
                    import json
                    social_data = json.loads(row[0])
                    title = social_data.get("etsy_title", "").split("|")[0].strip()
                except:
                    title = row[2].split("/")[-2].replace("_", " ") if "/" in row[2] else f"Ürün #{i}"
                scheduled.append({"title": title[:40], "time": row[6]})
    
    if not scheduled:
        await update.message.reply_text("📅 Planlanmış gönderi yok.\nÜrün seçmek için /pick yazın.")
        return
    
    msg = "📅 PLANLANMIŞ GÖNDERİLER:\n\n"
    for s in scheduled:
        from datetime import datetime, timedelta
        try:
            dt = datetime.fromisoformat(s["time"])
            est_str = (dt - timedelta(hours=5)).strftime("%d/%m %H:%M EST")
            tr_str = (dt + timedelta(hours=3)).strftime("%d/%m %H:%M TR")
            msg += f"• {s['title']}\n  ⏰ {est_str} ({tr_str})\n\n"
        except:
            msg += f"• {s['title']}\n  ⏰ {s['time']}\n\n"
    
    await update.message.reply_text(msg)
