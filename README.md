# Deathlipse AI Bot 🦇
**%100 Ücretsiz Yapay Zeka Destekli Video Otomasyon Botu**

Bu proje, Printify'daki ürünleri (özellikle alternatif, gotik ve metal giyim) alıp hiçbir bütçe gerektirmeden yapay zeka ile profesyonel pazarlama videolarına dönüştüren ve bunları otomatik olarak sosyal medyada paylaşan tam otomatik bir sistemdir.

## Özellikler
- **Printify Entegrasyonu:** Dükkandaki ürün görsellerini ve ID'lerini otomatik çeker.
- **Groq AI Prompt Üretimi:** Ürünün tasarımına göre Groq'un ultra hızlı yapay zekasını (Llama3) kullanarak harika promptlar yazar.
- **Yapay Zeka Video Üretimi (Hugging Face Spaces):** HF Spaces API'lerini (Gradio) arka planda ücretsiz kullanarak (Kling-AI, Luma vb.) durağan görselleri 3 saniyelik sinematik videolara (reels formatında) çevirir.
- **Müzik ve Ses İşleme:** FFmpeg kullanarak videoyu uygun formata sokar.
- **Telegram Onay Mekanizması:** Yayınlanacak videolar direkt olarak Telegram'a düşer. Kullanıcı tek tıkla onaylar veya reddeder.
- **Zernio API ile Otomatik Yayın:** Onaylanan videolar aynı anda **TikTok** ve **Instagram Reels**'a (ve istenirse Pinterest'e) telifsiz bir şekilde yayınlanır.

## Kurulum

1. Bilgisayarına **Python 3.10+** ve **FFmpeg** kur.
2. Bu depoyu indir:
   ```bash
   git clone https://github.com/SalihSay/deathlipse-bot.git
   cd deathlipse-bot
   ```
3. Gerekli kütüphaneleri yükle:
   ```bash
   pip install -r requirements.txt
   ```
4. Gizli anahtarlarını girmek için ana dizinde bir `.env` dosyası oluştur ve içini şöyle doldur:
   ```env
   # API Keys
   PRINTIFY_TOKEN=senin_printify_tokenin
   GROQ_API_KEY=senin_groq_tokenin
   
   # Telegram
   TELEGRAM_BOT_TOKEN=senin_bot_tokenin
   TELEGRAM_GROUP_ID=grup_id
   
   # Zernio
   ZERNIO_API_KEY=senin_zernio_anahtarin
   ZERNIO_TIKTOK_ACCOUNT_ID=tiktok_id
   ZERNIO_INSTAGRAM_ACCOUNT_ID=instagram_id
   ```

## Kullanım
Her gün düzenli bir şekilde ürün seçip video üretmesi için ana dosyayı çalıştır:
```bash
python main.py
```
Onay mekanizması için Telegram botunun arka planda sürekli çalışması gerekir:
```bash
python telegram_bot.py
```

## Güvenlik Notu
`bulk_schedule.csv`, `.env` ve anahtar (API Key) içeren tüm dosyalar gitignore ile gizlenmiştir. Proje tamamen güvenli şekilde açık kaynak olarak paylaşılmıştır.
