@echo off
echo =======================================
echo ORACLE CLOUD OTOMATIK KURULUM ARACI
echo =======================================
echo.
echo 1. Sunucuya baglaniliyor ve klasor olusturuluyor...
ssh -o StrictHostKeyChecking=no -i oracle_key.pem ubuntu@138.3.245.254 "mkdir -p ~/deathlipse-approval-bot"
echo.

echo 2. Dosyalar ve Klasorler kopyalaniyor...
scp -o StrictHostKeyChecking=no -i oracle_key.pem telegram_bot.py .env bulk_schedule.csv ubuntu@138.3.245.254:~/deathlipse-approval-bot/
scp -r -o StrictHostKeyChecking=no -i oracle_key.pem reels_output bulk_images ubuntu@138.3.245.254:~/deathlipse-approval-bot/
echo.

echo 3. Python gereksinimleri kuruluyor ve bot calistiriliyor...
ssh -o StrictHostKeyChecking=no -i oracle_key.pem ubuntu@138.3.245.254 "cd ~/deathlipse-approval-bot && sudo apt update -y && sudo apt install -y python3-pip python3-venv tmux && python3 -m venv venv && venv/bin/pip install \"python-telegram-bot[job-queue]\" requests python-dotenv && tmux kill-session -t deathlipse_bot 2>/dev/null; tmux new-session -d -s deathlipse_bot 'venv/bin/python telegram_bot.py'"
echo.
echo =======================================
echo TEBRIKLER! Kurulum basariyla tamamlandi.
echo Bot su an arka planda 7/24 calisiyor. Telegram'dan mesajlari bekleyin.
echo =======================================
pause
