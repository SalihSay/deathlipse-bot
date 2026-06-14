from datetime import time as dt_time, timezone
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from core.config import TELEGRAM_BOT_TOKEN
from bot.handlers import start, test_command, skip_current_command, status_command
from bot.approval import button_callback
from bot.scheduler import run_generator_job, reminder_job, check_token_expiry

def main():
    print("Starting Deathlipse Telegram Bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("skip_current", skip_current_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    job_queue = application.job_queue

    target_time_gen = dt_time(hour=7, minute=0, tzinfo=timezone.utc)
    job_queue.run_daily(run_generator_job, target_time_gen)

    reminders_utc = [
        dt_time(hour=9, minute=0, tzinfo=timezone.utc),
        dt_time(hour=12, minute=0, tzinfo=timezone.utc),
        dt_time(hour=15, minute=0, tzinfo=timezone.utc),
        dt_time(hour=18, minute=0, tzinfo=timezone.utc),
    ]
    for r_time in reminders_utc:
        job_queue.run_daily(reminder_job, r_time)

    job_queue.run_daily(check_token_expiry, dt_time(hour=6, minute=0, tzinfo=timezone.utc))

    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
