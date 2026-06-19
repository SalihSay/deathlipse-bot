import os
import csv
from telegram import Update
from telegram.ext import ContextTypes
from core.config import CSV_FILE, TELEGRAM_GROUP_ID
from bot.approval import check_for_posts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Deathlipse Otomasyon Hub'ı Aktif! Her gün yeni post üretilecek ve onay bekleyecek.\n"
        "Komutlar:\n/test - Sıradaki bekleyen gönderiyi getirir\n"
        "/skip_current - Bekleyen gönderiyi atlar\n"
        "/status - Kuyruk durumunu gösterir"
    )

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Manuel test tetiklendi, sıradaki gönderi aranıyor...")
    await check_for_posts(context)

async def skip_current_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.approval import get_next_pending_post, update_status
    row, index = get_next_pending_post()
    if not row:
        await update.message.reply_text("Şu anda bekleyen (PENDING) hiçbir gönderi yok.")
        return
    import json
    try:
        social_data = json.loads(row[0])
        prod_id = social_data.get("product_id")
    except:
        prod_id = None
        
    if not prod_id:
        prod_id = row[2].split("/")[-1].replace("post_", "").replace(".jpg", "").replace(".png", "")
        
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
