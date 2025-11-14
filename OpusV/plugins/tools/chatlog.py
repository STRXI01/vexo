import asyncio
import random
import urllib.parse
from pyrogram import filters, errors, types
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Optional

from config import LOGGER_ID
from OpusV import app

BOT_INFO: Optional[types.User] = None
BOT_ID: Optional[int] = None

PHOTOS = "https://files.catbox.moe/9pjp03.jpg"

# Message templates
JOIN_MESSAGE_TEMPLATE = (
    "✫ ɴᴇᴡ ɢʀᴏᴜᴘ\n\n"
    "🍀 ᴄʜᴀᴛ ɴᴀᴍᴇ: `{chat_title}`\n"
    "ᴄʜᴀᴛ ɪᴅ: `{chat_id}`\n"
    "ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ: @{chat_username}\n"
    "ᴄʜᴀᴛ ʟɪɴᴋ: [ᴄʟɪᴄᴋ ʜᴇʀᴇ]({invite_link})\n"
    "ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs: `{member_count}`\n"
    "🍃 ᴀᴅᴅᴇᴅ ʙʏ: {added_by}"
)

LEFT_MESSAGE_TEMPLATE = (
    "✫ <u>#ʟᴇғᴛ_ɢʀᴏᴜᴘ</u>\n\n"
    "📌 ᴄʜᴀᴛ ɴᴀᴍᴇ: `{chat_title}`\n"
    "ᴄʜᴀᴛ ɪᴅ: `{chat_id}`\n"
    "ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ: @{chat_username}\n"
    "💢 ʀᴇᴍᴏᴠᴇᴅ ʙʏ: {removed_by}\n"
    "ʙᴏᴛ: @{bot_username}"
)

def _is_valid_url(url: Optional[str]) -> bool:
    """Validate if a URL is properly formatted."""
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url.strip())
        return parsed.scheme in ("http", "https", "tg") and (parsed.netloc or parsed.path)
    except Exception:
        return False

async def _ensure_bot_info() -> None:
    """Ensure bot information is loaded."""
    global BOT_INFO, BOT_ID
    if BOT_INFO is None:
        try:
            BOT_INFO = await app.get_me()
            BOT_ID = BOT_INFO.id
        except Exception as e:
            print(f"Failed to get bot info: {e}")

async def _get_chat_member_count(chat_id: int) -> str:
    """Get chat member count with error handling."""
    try:
        count = await app.get_chat_members_count(chat_id)
        return str(count)
    except errors.FloodWait as fw:
        await asyncio.sleep(fw.value + 1)
        try:
            count = await app.get_chat_members_count(chat_id)
            return str(count)
        except Exception:
            return "?"
    except Exception:
        return "?"

async def _get_invite_link(chat_id: int) -> Optional[str]:
    """Get chat invite link with error handling."""
    try:
        return await app.export_chat_invite_link(chat_id)
    except Exception:
        return None

def _format_chat_username(username: Optional[str]) -> str:
    """Format chat username for display."""
    return username if username else "Private"

def _format_user_mention(user: Optional[types.User]) -> str:
    """Format user mention for display."""
    return user.mention if user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"

async def safe_send_photo(chat_id, photo, caption, reply_markup=None, max_retries=3):
    """Send photo with retry mechanism and error handling."""
    for attempt in range(max_retries):
        try:
            return await app.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )
        except errors.FloodWait as e:
            await asyncio.sleep(e.value + 1)
        except errors.ButtonUrlInvalid:
            return await app.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption
            )
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to send photo after {max_retries} attempts: {e}")
                raise
            await asyncio.sleep(1)

async def safe_send_message(chat_id, text, max_retries=3):
    """Send message with retry mechanism and error handling."""
    for attempt in range(max_retries):
        try:
            return await app.send_message(chat_id, text)
        except errors.FloodWait as e:
            await asyncio.sleep(e.value + 1)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to send message after {max_retries} attempts: {e}")
            await asyncio.sleep(1)

@app.on_message(filters.new_chat_members)
async def join_watcher(_, message: Message):
    """Handle bot joining new chats."""
    try:
        await _ensure_bot_info()
        if BOT_INFO is None or BOT_ID is None:
            return

        chat = message.chat
        
        for member in message.new_chat_members:
            if member.id != BOT_ID:
                continue

            # Gather chat information
            invite_link = await _get_invite_link(chat.id)
            member_count = await _get_chat_member_count(chat.id)
            
            # Format message
            caption = JOIN_MESSAGE_TEMPLATE.format(
                chat_title=chat.title,
                chat_id=chat.id,
                chat_username=_format_chat_username(chat.username),
                invite_link=invite_link or "https://t.me/",
                member_count=member_count,
                added_by=_format_user_mention(message.from_user)
            )

            # Create reply markup if invite link is valid
            reply_markup = None
            if _is_valid_url(invite_link):
                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("sᴇᴇ ɢʀᴏᴜᴘ 👀", url=invite_link.strip())]]
                )

            await safe_send_photo(
                LOGGER_ID,
                photo=PHOTOS,
                caption=caption,
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error in join_watcher: {e}")

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    """Handle bot leaving chats."""
    try:
        await _ensure_bot_info()
        if BOT_INFO is None or BOT_ID is None:
            return

        if message.left_chat_member.id != BOT_ID:
            return

        chat = message.chat
        
        # Format message
        text = LEFT_MESSAGE_TEMPLATE.format(
            chat_title=chat.title,
            chat_id=chat.id,
            chat_username=_format_chat_username(chat.username),
            removed_by=_format_user_mention(message.from_user),
            bot_username=BOT_INFO.username
        )

        await safe_send_message(LOGGER_ID, text)
    except Exception as e:
        print(f"Error while taking on_left_chat_member: {e}")
