from datetime import time as dt_time, timezone
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from core.config import TELEGRAM_BOT_TOKEN
from bot.handlers import start, pick_command, status_command, scheduled_command
from bot.approval import button_callback
from bot.scheduler import reminder_job, check_token_expiry
from bot.publisher import scheduled_publish_job

def main():
    print("Starting Deathlipse Telegram Bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pick", pick_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("scheduled", scheduled_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    job_queue = application.job_queue

    # Zamanlı yayın kontrolü — her 15 dakikada bir
    job_queue.run_repeating(scheduled_publish_job, interval=900, first=60)

    # Günlük hatırlatma — "Bugün ürün seçtin mi?"
    reminder_time = dt_time(hour=15, minute=0, tzinfo=timezone.utc)  # 18:00 TR
    job_queue.run_daily(reminder_job, reminder_time)

    # Token süresi kontrolü
    job_queue.run_daily(check_token_expiry, dt_time(hour=6, minute=0, tzinfo=timezone.utc))

    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
