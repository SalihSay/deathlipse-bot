Write-Host "DEATHLIPSE ORACLE CLOUD DEPLOYMENT"
Write-Host "=================================="

$REMOTE_USER = "ubuntu"
$REMOTE_IP = "138.3.245.254"
$KEY_PATH = "oracle_key.pem"
$REMOTE_DIR = "~/deathlipse-approval-bot"

# Fix SSH Key Permissions on Windows
Write-Host "SSH anahtar izinleri ayarlanıyor..."
icacls $KEY_PATH /inheritance:r /grant:r "$($env:USERNAME):F" | Out-Null

Write-Host "Adım 1: Sunucuda izole klasör oluşturuluyor..."
ssh -i $KEY_PATH -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_IP "mkdir -p $REMOTE_DIR"

Write-Host "Adım 2: Sosyal Medya dosyaları ve kodlar kopyalanıyor (Biraz zaman alabilir)..."
# Dosyaları tek tek gönder (Hata oranını düşürmek için)
scp -i $KEY_PATH -o StrictHostKeyChecking=no telegram_bot.py $REMOTE_USER@${REMOTE_IP}:$REMOTE_DIR/
scp -i $KEY_PATH -o StrictHostKeyChecking=no .env $REMOTE_USER@${REMOTE_IP}:$REMOTE_DIR/
scp -i $KEY_PATH -o StrictHostKeyChecking=no bulk_schedule.csv $REMOTE_USER@${REMOTE_IP}:$REMOTE_DIR/
scp -i $KEY_PATH -r -o StrictHostKeyChecking=no reels_output $REMOTE_USER@${REMOTE_IP}:$REMOTE_DIR/
scp -i $KEY_PATH -r -o StrictHostKeyChecking=no bulk_images $REMOTE_USER@${REMOTE_IP}:$REMOTE_DIR/

Write-Host "Adım 3: Dosyalar başarıyla aktarıldı!"
Write-Host ""
Write-Host "--- KURULUM VE BAŞLATMA TALİMATLARI ---"
Write-Host "1. Sunucuya bağlanmak için aşağıdaki komutu girin:"
Write-Host "ssh -i oracle_key.pem ubuntu@138.3.245.254"
Write-Host ""
Write-Host "2. Bağlandıktan sonra (ubuntu@ sunucusuna düştükten sonra) sırasıyla şunları yazın:"
Write-Host "cd deathlipse-approval-bot"
Write-Host "sudo apt update && sudo apt install python3-pip tmux -y"
Write-Host "pip3 install python-telegram-bot requests python-dotenv"
Write-Host "tmux new -s deathlipse_bot"
Write-Host "python3 telegram_bot.py"
Write-Host ""
Write-Host "(Not: tmux içindeyken botu arkada bırakıp çıkmak için önce CTRL+B sonra D tuşlarına basın)"
