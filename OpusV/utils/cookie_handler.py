import os
import time
import requests
from config import COOKIE_URL
from OpusV.utils.errors import capture_internal_err

COOKIE_PATH = "OpusV/resources/cookies.txt"
TIMESTAMP_PATH = "OpusV/resources/cookie_refresh_time.txt"
REFRESH_INTERVAL = 72 * 60 * 60  # 72 hours in seconds


def resolve_raw_cookie_url(url: str) -> str:
    """
    Return the raw content URL from Batbin, Pastebin, or direct .txt link.
    Supports:
    - https://batbin.me/abc123
    - https://pastebin.com/abc123
    - https://yourhost.com/path/cookies.txt (direct)
    """
    url = url.strip()
    low_url = url.lower()
    if "pastebin.com/" in low_url and "/raw/" not in low_url:
        paste_id = url.split("/")[-1]
        return f"https://pastebin.com/raw/{paste_id}"
    if "batbin.me/" in low_url and "/raw/" not in low_url:
        paste_id = url.split("/")[-1]
        return f"https://batbin.me/raw/{paste_id}"
    return url  # Direct .txt URL


def _needs_refresh() -> bool:
    """
    Check if 72 hours have passed since the last refresh.
    """
    if not os.path.exists(TIMESTAMP_PATH):
        return True

    try:
        with open(TIMESTAMP_PATH, "r") as f:
            last_refresh = float(f.read().strip())
    except Exception:
        return True

    return (time.time() - last_refresh) >= REFRESH_INTERVAL


def _update_refresh_time():
    """Update the refresh timestamp."""
    try:
        with open(TIMESTAMP_PATH, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


@capture_internal_err
async def fetch_and_store_cookies(force: bool = False):
    """
    Fetch cookies from resolved URL (Pastebin, Batbin, or direct .txt),
    then save them to the local cookies.txt file.
    Auto-refresh every 72 hours.
    """
    if not COOKIE_URL:
        raise EnvironmentError("⚠️ ᴄᴏᴏᴋɪᴇ_ᴜʀʟ ɴᴏᴛ sᴇᴛ ɪɴ ᴇɴᴠ.")

    # Skip if cookies are still valid
    if not force and not _needs_refresh() and os.path.exists(COOKIE_PATH):
        return  # Already valid, no refresh needed

    raw_url = resolve_raw_cookie_url(COOKIE_URL)

    try:
        response = requests.get(raw_url)
        response.raise_for_status()
    except Exception as e:
        raise ConnectionError(f"⚠️ ᴄᴀɴ'ᴛ ꜰᴇᴛᴄʜ ᴄᴏᴏᴋɪᴇs:\n{e}")

    cookies = response.text.strip()

    if not cookies.startswith("# Netscape"):
        raise ValueError("⚠️ ɪɴᴠᴀʟɪᴅ ᴄᴏᴏᴋɪᴇ ꜰᴏʀᴍᴀᴛ. ɴᴇᴇᴅs ɴᴇᴛsᴄᴀᴘᴇ ꜰᴏʀᴍᴀᴛ.")

    if len(cookies) < 100:
        raise ValueError("⚠️ ᴄᴏᴏᴋɪᴇ ᴄᴏɴᴛᴇɴᴛ ᴛᴏᴏ sʜᴏʀᴛ. ᴘᴏssɪʙʟʏ ɪɴᴠᴀʟɪᴅ.")

    try:
        # Delete old cookie file if exists
        if os.path.exists(COOKIE_PATH):
            os.remove(COOKIE_PATH)

        with open(COOKIE_PATH, "w", encoding="utf-8") as f:
            f.write(cookies)

        _update_refresh_time()
    except Exception as e:
        raise IOError(f"⚠️ ғᴀɪʟᴇᴅ ᴛᴏ sᴀᴠᴇ ᴄᴏᴏᴋɪᴇs: {e}")
