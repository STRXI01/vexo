import time
import html
import json
import os
from typing import Dict, List
from collections import defaultdict

from pyrogram import filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message

from config import OWNER_ID, LOGGER_ID, SUPPORT_CHAT
from OpusV import LOGGER, app

__all__ = [
    "init_antispam",
    "antispam_filter",
    "toggle_antispam",
    "is_antispam_enabled",
    "global_antispam_handler",
]

# Configuration
SPAM_THRESHOLD = 7  # Max allowed commands per BLOCK_TIME
BLOCK_TIME = 300   # Time window in seconds
UNBAN_AFTER = 1800  # Auto-unban after 1/2 hour
TG_BAN_FILE = "tgban.json"
user_records: Dict[str, List[float]] = defaultdict(list)
banned_users: Dict[int, float] = {}  # user_id -> ban_timestamp
ANTISPAM_ENABLED = False

# Load & Save Functions
def load_banned_users():
    global banned_users
    if not os.path.exists(TG_BAN_FILE):
        with open(TG_BAN_FILE, "w") as f:
            json.dump({}, f)
        banned_users = {}
        return

    try:
        with open(TG_BAN_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                banned_users = {int(k): float(v) for k, v in data.items()}
            elif isinstance(data, list):
                # Convert old format to new format
                current_time = time.time()
                banned_users = {user_id: current_time for user_id in data}
                save_banned_users()
            else:
                banned_users = {}
    except Exception:
        banned_users = {}
        with open(TG_BAN_FILE, "w") as f:
            json.dump({}, f)

def save_banned_users():
    try:
        with open(TG_BAN_FILE, "w") as f:
            json.dump(banned_users, f)
    except Exception as e:
        LOGGER("AntiSpam").error(f"Failed to save tgban.json: {e}")

def cleanup_expired_bans():
    """Remove users who have been banned for more than UNBAN_AFTER seconds"""
    global banned_users
    current_time = time.time()
    expired_users = [
        user_id for user_id, ban_time in banned_users.items()
        if current_time - ban_time > UNBAN_AFTER
    ]
    
    for user_id in expired_users:
        del banned_users[user_id]
    
    if expired_users:
        save_banned_users()
        LOGGER("AntiSpam").info(f"Auto-unbanned {len(expired_users)} expired users")

# Setup & Controls
def init_antispam():
    load_banned_users()
    cleanup_expired_bans()

def antispam_filter() -> filters.Filter:
    return filters.regex(r"^/") & (filters.private | filters.group)

def toggle_antispam(enable: bool) -> str:
    global ANTISPAM_ENABLED
    ANTISPAM_ENABLED = enable
    return "ENABLED ✅" if enable else "DISABLED ❌"

def is_antispam_enabled() -> bool:
    return ANTISPAM_ENABLED

# Helper Functions
async def _get_invite_link(chat) -> str | None:
    if chat.username:
        return f"https://t.me/{chat.username}"
    try:
        return await app.export_chat_invite_link(chat.id)
    except Exception:
        return None

# Management Commands
@app.on_message(filters.command(["clearspambans"]) & filters.user(OWNER_ID))
async def clear_spam_bans(_, message: Message):
    global banned_users
    count = len(banned_users)
    banned_users.clear()
    save_banned_users()
    await message.reply_text(f"✅ Cleared {count} antispam banned users.")

@app.on_message(filters.command(["spamstatus"]) & filters.user(OWNER_ID))
async def spam_status(_, message: Message):
    cleanup_expired_bans()  # Clean up before showing status
    
    status = "🟢 Enabled" if ANTISPAM_ENABLED else "🔴 Disabled"
    banned_count = len(banned_users)
    
    # Show some banned users info
    user_list = ""
    if banned_users:
        current_time = time.time()
        count = 0
        for user_id, ban_time in list(banned_users.items())[:5]:
            count += 1
            remaining = UNBAN_AFTER - (current_time - ban_time)
            if remaining > 0:
                user_list += f"\n{count}. {user_id} (unbans in {int(remaining)}s)"
            else:
                user_list += f"\n{count}. {user_id} (expired)"
        
        if len(banned_users) > 5:
            user_list += f"\n... and {len(banned_users) - 5} more"
    
    text = (
        f"🛡️ Antispam Status\n\n"
        f"Status: {status}\n"
        f"Banned Users: {banned_count}\n"
        f"Spam Threshold: {SPAM_THRESHOLD} commands\n"
        f"Block Time: {BLOCK_TIME} seconds\n"
        f"Auto-unban After: {UNBAN_AFTER} seconds"
        f"{user_list}"
    )
    await message.reply_text(text)

@app.on_message(filters.command(["toggleantispam"]) & filters.user(OWNER_ID))
async def toggle_antispam_cmd(_, message: Message):
    global ANTISPAM_ENABLED
    ANTISPAM_ENABLED = not ANTISPAM_ENABLED
    status = toggle_antispam(ANTISPAM_ENABLED)
    await message.reply_text(f"🛡️ Antispam: {status}")

# Core Handler
async def global_antispam_handler(_, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id

    if not ANTISPAM_ENABLED or user_id in OWNER_ID:
        await message.continue_propagation()
        return

    # Clean up expired bans periodically
    cleanup_expired_bans()

    # Check if user is currently banned
    if user_id in banned_users:
        current_time = time.time()
        ban_time = banned_users[user_id]
        
        # Check if ban has expired
        if current_time - ban_time > UNBAN_AFTER:
            del banned_users[user_id]
            save_banned_users()
        else:
            # User is still banned
            remaining = UNBAN_AFTER - (current_time - ban_time)
            notify = (
                f"🚫 You are temporarily blocked for spamming.\n"
                f"⏰ Unban in: {int(remaining)} seconds\n"
                f"💬 Support: https://t.me/{SUPPORT_CHAT}"
            )
            await message.reply_text(notify, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            return

    chat_id = message.chat.id if message.chat else user_id
    key = f"{chat_id}:{user_id}"
    now = time.time()
    timestamps = user_records[key]
    timestamps[:] = [t for t in timestamps if now - t < BLOCK_TIME]
    timestamps.append(now)

    if len(timestamps) > SPAM_THRESHOLD:
        banned_users[user_id] = now
        save_banned_users()

        notify = (
            f"🚫 You have been temporarily blocked for spamming.\n"
            f"⏰ Duration: {UNBAN_AFTER // 60} minutes\n"
            f"💬 Support: https://t.me/{SUPPORT_CHAT}"
        )
        await message.reply_text(notify, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        # Prepare chat info for logging
        if message.chat:
            chat = message.chat
            ct = chat.type
            chat_title = html.escape(getattr(chat, "title", "Private Chat"))
            lines = [f"📌 Chat Type: {ct.name.title()}"]
            if ct is ChatType.PRIVATE:
                user_name = html.escape(chat.first_name or "User")
                username = f"@{chat.username}" if chat.username else "N/A"
                lines.append(f"👤 User: <a href='tg://user?id={chat.id}'>{user_name}</a>")
                lines.append(f"🔗 Username: {username}")
            else:
                lines.append(f"🏷️ Title: {chat_title}")
                username_link = f"<a href='https://t.me/{chat.username}'>@{chat.username}</a>" if chat.username else None
                if username_link:
                    lines.append(f"🔗 Username: {username_link}")
                invite = await _get_invite_link(chat)
                if invite:
                    lines.append(f"📩 Invite: <a href='{invite}'>Link</a>")
            lines.append(f"🆔 ID: <code>{chat.id}</code>")
            chat_info = "\n".join(lines) + "\n"
        else:
            chat_info = "⚠️ Chat info unavailable\n"

        log = (
            "🚨 Spammer Detected\n\n"
            f"👤 User: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> "
            f"(<code>{user_id}</code>)\n"
            f"🔗 Username: @{message.from_user.username or 'N/A'}\n"
            f"🗨️ Command: <code>{html.escape(message.text or '')[:50]}</code>\n"
            f"⏰ Ban Duration: {UNBAN_AFTER // 60} minutes\n"
            f"{chat_info}"
        )
        await app.send_message(LOGGER_ID, log, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        return

    await message.continue_propagation()
