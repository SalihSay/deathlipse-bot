"""
Zamanlayıcı görevleri — günlük hatırlatma ve token süresi kontrolü.
"""
import os
from datetime import datetime
from telegram.ext import ContextTypes
from core.config import TELEGRAM_GROUP_ID
from bot.approval import get_all_pending_posts

async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    """Günde 1 kez hatırlatma — bekleyen ürün varsa bildir."""
    pending = get_all_pending_posts()
    if not pending:
        return
    
    msg = (
        f"📢 Günlük Hatırlatma!\n\n"
        f"Bekleyen {len(pending)} ürün var.\n"
        f"Bugün paylaşacağın ürünü seçmek için /pick yaz."
    )
    try:
        await context.bot.send_message(
            chat_id=TELEGRAM_GROUP_ID,
            text=msg
        )
    except Exception as e:
        print(f"Failed to send reminder: {e}")

async def check_token_expiry(context: ContextTypes.DEFAULT_TYPE):
    """Meta API token süresini kontrol eder."""
    issue_date_str = os.getenv("META_TOKEN_ISSUE_DATE", "")
    if not issue_date_str:
        print("[!] META_TOKEN_ISSUE_DATE bulunamadı, token süresi takip edilemiyor.")
        return
    try:
        issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
        current_date = datetime.now()
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
