import os
import asyncio
from datetime import datetime
from telegram.ext import ContextTypes
from core.config import TELEGRAM_GROUP_ID
from bot.approval import check_for_posts, get_next_pending_post

async def run_generator_job(context: ContextTypes.DEFAULT_TYPE):
    print("Running daily bulk content generator...")
    proc = await asyncio.create_subprocess_exec(
        "python", "bulk_content_generator.py",  "--batch", "1",
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

async def check_token_expiry(context: ContextTypes.DEFAULT_TYPE):
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
