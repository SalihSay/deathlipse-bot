import os
import paramiko
from scp import SCPClient

KEY_PATH = "oracle_key.pem"
HOST = "138.3.245.254"
USER = "ubuntu"
REMOTE_DIR = "deathlipse-approval-bot"

def create_ssh_client():
    key = paramiko.RSAKey.from_private_key_file(KEY_PATH)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 15 saniyelik timeout süresi
    ssh.connect(hostname=HOST, username=USER, pkey=key, timeout=15)
    return ssh

def main():
    print("Bulut sunucusuna bağlanılıyor...")
    try:
        ssh = create_ssh_client()
        print("Bağlantı başarılı!")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
        print("\n[!] LÜTFEN ŞUNU KONTROL EDİN:")
        print("Oracle Cloud -> Networking -> Virtual Cloud Networks -> VCN'inize tıklayın.")
        print("Security Lists kısmında Port 22'nin 0.0.0.0/0 (Tüm internet) için açık olduğundan emin olun.")
        return

    print(f"Sunucuda {REMOTE_DIR} klasörü oluşturuluyor...")
    ssh.exec_command(f"mkdir -p {REMOTE_DIR}")

    print("Dosyalar ve medya klasörleri yükleniyor (Bu işlem videoların boyutuna göre birkaç dakika sürebilir)...")
    try:
        with SCPClient(ssh.get_transport()) as scp:
            scp.put("telegram_bot.py", remote_path=f"{REMOTE_DIR}/")
            scp.put(".env", remote_path=f"{REMOTE_DIR}/")
            scp.put("bulk_schedule.csv", remote_path=f"{REMOTE_DIR}/")
            scp.put("reels_output", recursive=True, remote_path=f"{REMOTE_DIR}")
            scp.put("bulk_images", recursive=True, remote_path=f"{REMOTE_DIR}")
        print("Yükleme tamamlandı.")
    except Exception as e:
        print(f"Dosya yükleme hatası: {e}")

    print("Sunucuda gerekli Python kütüphaneleri kuruluyor ve bot başlatılıyor...")
    commands = [
        f"cd {REMOTE_DIR}",
        "sudo apt update -y",
        "sudo apt install python3-pip python3-venv tmux -y",
        "python3 -m venv venv",
        "venv/bin/pip install python-telegram-bot requests python-dotenv",
        "tmux kill-session -t deathlipse_bot 2>/dev/null || true",
        "tmux new-session -d -s deathlipse_bot 'venv/bin/python telegram_bot.py'"
    ]
    
    cmd = " && ".join(commands)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    if out:
        print("Çıktı:", out)
    if err:
        print("Hata:", err)
        
    print("\n✅ TEBRİKLER! Sistem başarıyla Oracle Cloud'a entegre edildi.")
    print("Telegram botu arka planda tmux ile çalışmaya başladı.")
    print("Birkaç saniye içinde Telegram kanalınıza ilk onay bildirimi düşecektir.")
    ssh.close()

if __name__ == '__main__':
    main()
