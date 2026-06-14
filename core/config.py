import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID", "")

# Zernio API (TikTok + Pinterest)
ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY", "")
ZERNIO_TIKTOK_ACCOUNT_ID = os.getenv("ZERNIO_TIKTOK_ACCOUNT_ID", "")
ZERNIO_PINTEREST_ACCOUNT_ID = os.getenv("ZERNIO_PINTEREST_ACCOUNT_ID", "")

# Meta Graph API (Instagram/Threads)
META_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
META_IG_USER_ID = os.getenv("META_IG_USER_ID", "")

# NVIDIA
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# Etsy
ETSY_API_KEY = os.getenv("ETSY_API_KEY", "")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
ETSY_SHOP_ID = os.getenv("ETSY_SHOP_ID", "")
ETSY_ACCESS_TOKEN = os.getenv("ETSY_ACCESS_TOKEN", "")

# Paths
CSV_FILE = "bulk_schedule.csv"
POSTED_JSON = "assets/posted_products.json"
