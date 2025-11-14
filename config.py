import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables from .env file
load_dotenv()

# ───── Basic Bot Configuration ───── #
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")

OWNER_ID = int(getenv("OWNER_ID", ))
OWNER_USERNAME = getenv("OWNER_USERNAME", "Akanesakuramori")
BOT_USERNAME = getenv("BOT_USERNAME", "Deltamusicrobot")
BOT_NAME = getenv("BOT_NAME", "Kawai ꭙ M𝗎𝗌𝗂𝖼 ˼")
ASSUSERNAME = getenv("ASSUSERNAME", "None")
EVALOP = list(map(int, getenv("EVALOP", "1852362865").split()))


# ───── Mongo & Logging ───── #
MONGO_DB_URI = getenv("MONGO_DB_URI")
LOGGER_ID = int(getenv("LOGGER_ID", -1002436267094))
SONG_DUMP_ID = "-1002436267094"
LOG_ERROR_ID = "-1002436267094"

# ───── Limits and Durations ───── #
RESTART_INTERVAL = int(getenv("RESTART_INTERVAL", 86400))  # default 24 hours
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

# ───── Custom API Configs ───── #
COOKIE_URL = getenv("COOKIE_URL") #necessary
API_URL = getenv("API_URL") #optional
API_KEY = getenv("API_KEY") #optional

# ───── Heroku Configuration ───── #
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# ───── Git & Updates ───── #
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/utkarshdubey2008/opus-main")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN")

# ───── Support & Community ───── #
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/TheAlphaBotz")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "AlphaBotzChat")

# ───── Assistant Auto Leave ───── #
AUTO_LEAVING_ASSISTANT = False
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "11500"))

# ───── Error Handling ───── #
DEBUG_IGNORE_LOG =True

# ───── Spotify Credentials ───── #
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "c9c63c6fbf2f467c8bc68624851e9773")

# ───── Session Strings ───── #
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

# ───── Server Settings ───── #
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "3000"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "400"))

AUTO_SUGGESTION_MODE = getenv("AUTO_SUGGESTION_MODE", "False")

AUTO_SUGGESTION_TIME = int(getenv("AUTO_SUGGESTION_TIME", "60"))

# ───── Bot Media Assets ───── #


START_VID = "https://files.catbox.moe/0t9ok0.mp4"

STICKERS = [
    "CAACAgQAAyEFAASRNnxWAAI1BGjaYTlj-m1uOD6GkLcNx6lvY3oHAAKtGgACZ2GpUWhy5629j6eVHgQ",
    "CAACAgQAAyEFAASRNnxWAAI1A2jaYTjWNcpOdEdvEV7blCwt02MMAAKqFwACIL-oUeHkxNZLo1ipHgQ",
    "CAACAgQAAyEFAASRNnxWAAI1AmjaYTdo4p_5P7zh2uiFF7PPNvZvAAJ1GwACDYKoUQpiUwZctQO6HgQ",
    "CAACAgQAAyEFAASRNnxWAAI1AWjaYTe9OPLILXAKbQP4pOXPAROLAAJGGwACZFupUXhNroQ9G8UxHgQ",
    "CAACAgQAAyEFAASRNnxWAAI1AAFo2mE2gMQdOB42st29hmw8jJA72QACixkAAjBMsVH89bbAktUj2x4E"
    "CAACAgQAAyEFAASRNnxWAAI1CGjaYT3ITXhsUDatvbbIgzrb8R2cAAKvGwAC_UKoUV8PBnMdHSrgHgQ",
    "CAACAgQAAyEFAASRNnxWAAI1CWjaYT-RNSP1Y2VM6vBqROBjrcvBAALlGwACOS-oUZNPjF5GnKbVHgQ"
]
START_IMG_URL = "https://files.catbox.moe/x47u79.jpg"
FAILED = "https://files.catbox.moe/6xpaz5.jpg"
HELP_IMG_URL = "https://files.catbox.moe/x47u79.jpg"
PING_IMG_URL = "https://files.catbox.moe/2wcsfs.jpg"
PLAYLIST_IMG_URL = "https://files.catbox.moe/7keo5k.jpg"
STATS_IMG_URL = "https://files.catbox.moe/tvw3pc.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/7i1dsp.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/7i1dsp.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/7i1dsp.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/7c4ib1.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/kwi3ck.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/64wva2.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/64wva2.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/64wva2.jpg"
APPLE_IMG_URL = "https://files.catbox.moe/cq87ww.jpg"

AYU = ["🎵", "🦋", "🚩", "☘️", "⚡️", "🦄", "🎩", "👀", "🛥", "🚂", "🐝", "🕊️", "⛈️", "💌", "✨"]

# ───── Utility & Functional ───── #
def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# ───── Runtime Structures ───── #
BANNED_USERS = filters.user()
adminlist, lyrical, votemode, autoclean, confirmer = {}, {}, {}, [], {}

# ───── URL Validation ───── #
if SUPPORT_CHANNEL and not re.match(r"^https?://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHANNEL URL. Must start with https://")

if SUPPORT_CHAT and not re.match(r"^https?://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHAT URL. Must start with https://")
