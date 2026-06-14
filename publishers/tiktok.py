from core.config import ZERNIO_TIKTOK_ACCOUNT_ID
from publishers.zernio import post as zernio_post

def post(caption, media_path, media_type="video"):
    config = [{"platform": "tiktok", "accountId": ZERNIO_TIKTOK_ACCOUNT_ID}]
    return zernio_post(caption, media_path, config, media_type)
