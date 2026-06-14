# Deathlipse Bot 🦇⚡

**Full-Stack AI-Powered E-Commerce Automation System**

An end-to-end autonomous content production and multi-platform publishing pipeline for the [Deathlipse](https://www.etsy.com/shop/Deathlipse) alternative/gothic fashion brand. Built with Python, running 24/7 on Oracle Cloud.

---

## Architecture Overview

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Etsy Store  │────▶│  Content Engine   │────▶│  Telegram Approval  │
│  (REST API)  │     │  (AI + Render)    │     │  (Async Bot)        │
└──────────────┘     └──────────────────┘     └──────┬──────────────┘
                                                      │ One-tap approve
                                              ┌───────▼───────┐
                                              │  Multi-Platform│
                                              │  Publisher     │
                                              └───┬───┬───┬───┘
                          ┌────────┬────────┬─────┘   │   └─────┬────────┐
                          ▼        ▼        ▼         ▼         ▼        ▼
                      Instagram  Instagram  TikTok  YouTube   Pinterest Threads
                       Reels      Story              Shorts
```

## Features

### 🔗 Etsy Integration & SEO Optimization
- Programmatic product fetching via **Etsy REST API** with OAuth 2.0 (PKCE flow)
- Batch SEO optimization of titles, descriptions, and tags for 59+ listings
- AI-generated sales copy using **NVIDIA NIM (Mistral Large 3)** for the US market

### 🎬 Autonomous Video Production
- AI background removal with **Rembg** (U²-Net)
- Pixel-perfect compositing via **NumPy** matrices and **Pillow (PIL)**
- AI-generated backgrounds using **Stable Diffusion** (no stock images)
- High-quality music integration with **yt-dlp**
- Cinematic video rendering with **OpenCV** and **MoviePy**

### 🤖 Telegram Command & Control
- Fully **async (asyncio)** architecture — never blocks during heavy renders
- Inline keyboard approval: one tap to publish, one tap to skip
- Real-time status reporting with per-platform success/failure indicators

### 📡 Multi-Platform Publishing (6 Platforms)
- **Instagram Reels** — Meta Graph API with `share_to_feed` support
- **Instagram Stories** — Meta Graph API
- **YouTube Shorts** — YouTube Data API v3 with auto-refresh OAuth tokens
- **TikTok** — Zernio API
- **Pinterest** — Zernio API
- **Threads** — Meta Threads API
- Media delivery via **tmpfiles.org** CDN for cloud-to-API file transfers

### ☁️ DevOps & Deployment
- **Oracle Cloud (OCI)** — Always-free tier VM running 24/7
- **SSH/SCP** automated deployment pipeline (`deploy.bat`)
- **tmux** persistent process management
- **Git/GitHub** version control with security-hardened `.gitignore`
- **Google OAuth 2.0** in Production mode — tokens never expire

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.10+ |
| **AI / ML** | NVIDIA NIM (Mistral Large 3), Stable Diffusion, Rembg (U²-Net) |
| **Video** | OpenCV, MoviePy, NumPy, Pillow, yt-dlp |
| **APIs** | Meta Graph API, YouTube Data API v3, Etsy REST API, Zernio API, Telegram Bot API |
| **Auth** | Google OAuth 2.0, Etsy OAuth 2.0 (PKCE) |
| **Cloud** | Oracle Cloud Infrastructure (OCI) |
| **DevOps** | SSH/SCP, tmux, Git/GitHub |
| **CDN** | tmpfiles.org (cloud-to-API media relay) |

---

## Project Structure

```
deathlipse-bot/
├── telegram_bot.py          # Core bot — approval flow & multi-platform publisher
├── video_generator.py       # AI video production pipeline
├── youtube_uploader.py      # YouTube Data API v3 integration with OAuth
├── bulk_content_generator.py# Batch content generation for all products
├── prompt_generator.py      # NVIDIA NIM AI prompt generation
├── programmatic_reels.py    # Automated reels creation engine
├── etsy_fetcher.py          # Etsy product data fetcher
├── fetch_etsy.py            # Etsy API utilities
├── etsy_oauth.py            # Etsy OAuth 2.0 PKCE authentication
├── etsy_optimizer.py        # Batch SEO optimization (titles/desc/tags)
├── etsy_optimizer_batch2.py # SEO optimization batch 2
├── auto_optimize_all.py     # Full catalog auto-optimization
├── download_music.py        # Royalty-free music downloader
├── yt_reauth.py             # YouTube token re-authentication utility
├── test_yt_refresh.py       # YouTube token health checker
├── deploy.bat               # One-click Oracle Cloud deployment script
├── requirements.txt         # Python dependencies
├── .env                     # API keys & tokens (gitignored)
├── client_secrets.json      # Google OAuth credentials (gitignored)
├── token.json               # YouTube OAuth token (gitignored)
├── oracle_key.pem           # SSH private key (gitignored)
├── bulk_schedule.csv        # Content publishing schedule (gitignored)
├── assets/
│   ├── fonts/               # Custom typography
│   ├── images/              # Product images (gitignored)
│   └── posted_products.json # Publishing history (gitignored)
├── bulk_images/             # Generated post images (gitignored)
└── reels_output/            # Rendered video files (gitignored)
```

---

## Setup

### Prerequisites
- Python 3.10+
- Oracle Cloud account (free tier works)

### Installation

```bash
git clone https://github.com/SalihSay/deathlipse-bot.git
cd deathlipse-bot
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_GROUP_ID=your_group_id

# Meta (Instagram/Threads)
META_PAGE_ACCESS_TOKEN=your_meta_token
META_IG_USER_ID=your_ig_user_id

# Zernio (TikTok + Pinterest)
ZERNIO_API_KEY=your_zernio_key
ZERNIO_TIKTOK_ACCOUNT_ID=your_tiktok_id
ZERNIO_PINTEREST_ACCOUNT_ID=your_pinterest_id

# NVIDIA NIM
NVIDIA_API_KEY=your_nvidia_key
```

Set up YouTube OAuth:
```bash
python yt_reauth.py
```

### Deploy to Oracle Cloud

```bash
deploy.bat
```

### Run Locally

```bash
python telegram_bot.py
```

---

## Security

All sensitive files are excluded from version control via `.gitignore`:
- `.env` — API keys and tokens
- `client_secrets.json` / `token.json` — Google OAuth credentials
- `oracle_key.pem` — SSH private key
- `etsy_token.json` — Etsy OAuth token
- `bulk_schedule.csv` — Product data
- `assets/images/` — Product images
- `*.mp4` — Generated videos

---

## License

This project is open source for educational and portfolio purposes.
