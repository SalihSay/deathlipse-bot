@echo off
echo =======================================
echo ORACLE CLOUD OTOMATIK KURULUM VE GUNCELLEME ARACI
echo =======================================
echo.
echo 1. Sunucuya baglaniliyor ve klasor yapilari kontrol ediliyor...
ssh -o StrictHostKeyChecking=no -i oracle_key.pem ubuntu@138.3.245.254 "mkdir -p ~/deathlipse-approval-bot/assets"
echo.

echo 2. Kod dosyaları (Git uzerinden) guncelleniyor...
ssh -o StrictHostKeyChecking=no -i oracle_key.pem ubuntu@138.3.245.254 "cd ~/deathlipse-approval-bot && git init && (git remote add origin https://github.com/SalihSay/deathlipse-bot.git 2>nul || echo Remote exists) && git fetch origin && git reset --hard origin/master"
echo.

echo 3. Local veriler ve medya dosyalari (media) kopyalaniyor...
echo (Bu islem medya boyutuna gore birkac dakika surebilir...)
scp -o StrictHostKeyChecking=no -i oracle_key.pem .env bulk_schedule.csv ubuntu@138.3.245.254:~/deathlipse-approval-bot/
scp -o StrictHostKeyChecking=no -i oracle_key.pem assets/posted_products.json ubuntu@138.3.245.254:~/deathlipse-approval-bot/assets/
scp -r -o StrictHostKeyChecking=no -i oracle_key.pem media ubuntu@138.3.245.254:~/deathlipse-approval-bot/
echo.

echo 4. Python gereksinimleri kuruluyor ve bot (main.py) baslatiliyor...
ssh -o StrictHostKeyChecking=no -i oracle_key.pem ubuntu@138.3.245.254 "cd ~/deathlipse-approval-bot && sudo apt update -y && sudo apt install -y python3-pip python3-venv tmux && python3 -m venv venv && venv/bin/pip install -r requirements.txt && tmux kill-session -t deathlipse_bot 2>/dev/null; tmux new-session -d -s deathlipse_bot 'venv/bin/python main.py'"
echo.
echo =======================================
echo TEBRIKLER! Guncelleme basariyla tamamlandi.
echo Yeni bot (main.py uzerinden) su an arka planda 7/24 calisiyor.
echo =======================================
pause
