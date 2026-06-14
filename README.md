# Deathlipse Bot 🦇⚡

**Yapay Zeka Destekli Tam Kapsamlı E-Ticaret Otomasyon Sistemi**

[Deathlipse](https://www.etsy.com/shop/Deathlipse) alternatif/gotik moda markası için uçtan uca otonom içerik üretim ve çoklu platform yayın pipeline'ı. Python ile geliştirildi, Oracle Cloud üzerinde 7/24 çalışıyor.

---

## Mimari Genel Bakış

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Etsy Mağaza │────▶│  İçerik Motoru   │────▶│  Telegram Onay      │
│  (REST API)  │     │  (AI + Render)    │     │  (Asenkron Bot)     │
└──────────────┘     └──────────────────┘     └──────┬──────────────┘
                                                      │ Tek dokunuşla onayla
                                              ┌───────▼───────┐
                                              │  Çoklu Platform│
                                              │  Yayıncı       │
                                              └───┬───┬───┬───┘
                          ┌────────┬────────┬─────┘   │   └─────┬────────┐
                          ▼        ▼        ▼         ▼         ▼        ▼
                      Instagram  Instagram  TikTok  YouTube   Pinterest Threads
                       Reels      Story              Shorts
```

## Özellikler

### 🔗 Etsy Entegrasyonu & SEO Optimizasyonu
- **Etsy REST API** üzerinden OAuth 2.0 (PKCE akışı) ile programatik ürün çekme
- 59+ ürün için başlık, açıklama ve etiketlerin toplu SEO optimizasyonu
- ABD pazarı için **NVIDIA NIM (Mistral Large 3)** ile yapay zeka destekli satış metni üretimi

### 🎬 Otonom Video Üretimi
- **Rembg** (U²-Net) ile yapay zeka destekli arka plan kaldırma
- **NumPy** matrisleri ve **Pillow (PIL)** ile piksel düzeyinde kusursuz birleştirme
- **Stable Diffusion** ile yapay zeka tarafından üretilen arka planlar (stok görsel kullanılmadı)
- **yt-dlp** ile yüksek kaliteli müzik entegrasyonu
- **OpenCV** ve **MoviePy** ile sinematik video render

### 🤖 Telegram Komuta & Kontrol Merkezi
- Tamamen **asenkron (asyncio)** mimari — ağır render işlemlerinde asla kilitlenmiyor
- Satır içi klavye onayı: yayınlamak için tek dokunuş, atlamak için tek dokunuş
- Platform bazlı başarı/başarısızlık göstergeleri ile gerçek zamanlı durum raporlama

### 📡 Çoklu Platform Yayını (6 Platform)
- **Instagram Reels** — Meta Graph API, `share_to_feed` desteği ile
- **Instagram Stories** — Meta Graph API
- **YouTube Shorts** — YouTube Data API v3, otomatik yenilenen OAuth token'lar
- **TikTok** — Zernio API
- **Pinterest** — Zernio API
- **Threads** — Meta Threads API
- Buluttan API'ye dosya transferi için **tmpfiles.org** CDN entegrasyonu

### ☁️ DevOps & Deployment
- **Oracle Cloud (OCI)** — Her zaman ücretsiz tier VM üzerinde 7/24 çalışıyor
- **SSH/SCP** otomatik deployment pipeline'ı (`deploy.bat`)
- **tmux** kalıcı süreç yönetimi
- Güvenlik odaklı `.gitignore` ile **Git/GitHub** versiyon kontrolü
- Production modunda **Google OAuth 2.0** — token'lar asla sona ermez

---

## Teknoloji Yığını

| Kategori | Teknolojiler |
|----------|-------------|
| **Dil** | Python 3.10+ |
| **AI / ML** | NVIDIA NIM (Mistral Large 3), Stable Diffusion, Rembg (U²-Net) |
| **Video** | OpenCV, MoviePy, NumPy, Pillow, yt-dlp |
| **API'ler** | Meta Graph API, YouTube Data API v3, Etsy REST API, Zernio API, Telegram Bot API |
| **Kimlik Doğrulama** | Google OAuth 2.0, Etsy OAuth 2.0 (PKCE) |
| **Bulut** | Oracle Cloud Infrastructure (OCI) |
| **DevOps** | SSH/SCP, tmux, Git/GitHub |
| **CDN** | tmpfiles.org (buluttan API'ye medya aktarımı) |

---

## Proje Yapısı

```
deathlipse-bot/
├── main.py                       # Tek giriş noktası — Telegram botunu başlatır
├── README.md
├── requirements.txt
├── .env                          # API anahtarları ve token'lar (gitignore)
├── .gitignore
│
├── core/                         # Ortak altyapı modülleri
│   ├── config.py                 # Tüm ortam değişkenleri ve sabitler
│   └── uploader.py               # tmpfiles.org CDN yükleme fonksiyonu
│
├── publishers/                   # Platform yayın modülleri
│   ├── instagram.py              # Meta Graph API (Reels + Story)
│   ├── youtube.py                # YouTube Data API v3
│   ├── threads.py                # Threads API
│   ├── zernio.py                 # Zernio API ortak altyapısı
│   ├── tiktok.py                 # Zernio TikTok
│   └── pinterest.py              # Zernio Pinterest
│
├── etsy/                         # Etsy entegrasyonu
│   ├── fetcher.py                # Ürün verisi çekme
│   ├── auth.py                   # OAuth 2.0 PKCE kimlik doğrulama
│   └── optimizer.py              # Toplu SEO optimizasyonu
│
├── content/                      # İçerik üretim pipeline'ı
│   ├── video_generator.py        # OpenCV + MoviePy video render
│   ├── prompt_generator.py       # NVIDIA NIM AI metin üretimi
│   ├── reels_engine.py           # Otomatik reels oluşturma motoru
│   └── music_downloader.py       # yt-dlp müzik indirme
│
├── bot/                          # Telegram bot mantığı
│   ├── handlers.py               # Komut handler'ları (/test, /status, /skip)
│   ├── scheduler.py              # Günlük iş zamanlama
│   └── approval.py               # Onay/ret callback ve yayın orkestrasyon
│
├── scripts/                      # Yardımcı araçlar
│   ├── deploy.bat                # Oracle Cloud tek tıkla deployment
│   ├── yt_reauth.py              # YouTube token yeniden yetkilendirme
│   └── test_yt_refresh.py        # YouTube token sağlık kontrolü
│
└── assets/                       # Statik dosyalar
    ├── fonts/                    # Özel tipografi
    ├── audio/                    # Müzik dosyaları (gitignore)
    └── images/                   # Ürün görselleri (gitignore)
```

---

## Kurulum

### Gereksinimler
- Python 3.10+
- Oracle Cloud hesabı (ücretsiz tier yeterli)

### Yükleme

```bash
git clone https://github.com/SalihSay/deathlipse-bot.git
cd deathlipse-bot
pip install -r requirements.txt
```

### Yapılandırma

Proje kök dizininde bir `.env` dosyası oluşturun:

```env
# Telegram
TELEGRAM_BOT_TOKEN=sizin_bot_tokeniniz
TELEGRAM_GROUP_ID=sizin_grup_idniz

# Meta (Instagram/Threads)
META_PAGE_ACCESS_TOKEN=sizin_meta_tokeniniz
META_IG_USER_ID=sizin_ig_kullanici_idniz

# Zernio (TikTok + Pinterest)
ZERNIO_API_KEY=sizin_zernio_anahtariniz
ZERNIO_TIKTOK_ACCOUNT_ID=sizin_tiktok_idniz
ZERNIO_PINTEREST_ACCOUNT_ID=sizin_pinterest_idniz

# NVIDIA NIM
NVIDIA_API_KEY=sizin_nvidia_anahtariniz
```

YouTube OAuth kurulumu:
```bash
python scripts/yt_reauth.py
```

### Oracle Cloud'a Deployment

```bash
scripts/deploy.bat
```

### Lokalde Çalıştırma

```bash
python main.py
```

---

## Güvenlik

Tüm hassas dosyalar `.gitignore` ile versiyon kontrolünden hariç tutulmuştur:
- `.env` — API anahtarları ve token'lar
- `client_secrets.json` / `token.json` — Google OAuth kimlik bilgileri
- `oracle_key.pem` — SSH özel anahtarı
- `etsy_token.json` — Etsy OAuth token'ı
- `bulk_schedule.csv` — Ürün verileri
- `assets/images/` — Ürün görselleri
- `*.mp4` — Üretilen videolar

---

## Lisans

Bu proje eğitim ve portföy amaçlı açık kaynak olarak paylaşılmıştır.
