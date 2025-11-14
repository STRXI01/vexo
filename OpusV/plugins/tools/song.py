# song.py
import os
import re
import uuid
import asyncio
import tempfile
import httpx

from pyrogram import filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
    Message,
)

from OpusV import app
from config import (
    BANNED_USERS,
    SONG_DOWNLOAD_DURATION,
    SONG_DOWNLOAD_DURATION_LIMIT,
    SONG_DUMP_ID,
    LOGGER_ID,
)
from OpusV.utils.decorators.language import language, languageCB
from OpusV.utils.errors import capture_err, capture_callback_err
from OpusV.utils.formatters import convert_bytes, time_to_seconds
from OpusV.utils.inline.song import song_markup
from OpusV.utils.database import is_on_off, get_spam_data, add_spam_data, block_user

SONG_COMMAND = ["song", "music"]

# In-memory store mapping short keys -> track metadata (spotify_url, name, artist, cover, duration, download_url)
# This keeps callback_data small (we pass only the short key). It's ephemeral (cleared on restart).
TRACK_STORE = {}

BILLA_API_BASE = "https://billa-api.vercel.app"


class InlineKeyboardBuilder(list):
    def row(self, *buttons):
        self.append(list(buttons))


@app.on_message(filters.command(SONG_COMMAND) & filters.group & ~BANNED_USERS)
@capture_err
@language
async def song_command_group(client, message: Message, lang):
    await message.reply_text(
        lang["song_1"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(lang["SG_B_1"],
                                   url=f"https://t.me/{app.username}?start=song")]]
        ),
    )


@app.on_message(filters.command(SONG_COMMAND) & filters.private & ~BANNED_USERS)
@capture_err
@language
async def song_command_private(client, message: Message, lang):
    """
    Replaces YouTube-based search/details with Billa API search.
    We search for the user's query via the API and present the top result (if any).
    The callback buttons reference a short key stored in TRACK_STORE to fetch download_url later.
    """
    await message.delete()
    mystic = await message.reply_text(lang["play_1"])

    # extract query text (same behavior as before)
    query = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not query:
        return await mystic.edit_text(lang["song_2"])

    # Use Billa API search endpoint
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{BILLA_API_BASE}/search_track/{httpx.utils.quote(query)}")
            if resp.status_code != 200:
                return await mystic.edit_text(lang["play_3"])
            data = resp.json()
    except Exception:
        return await mystic.edit_text(lang["play_3"])

    results = data.get("results") or []
    if not results:
        return await mystic.edit_text(lang["song_5"])

    # pick the first/top result (you can modify to show multiple)
    r = results[0]
    # expected keys: id, name, artist, cover, cover_small, duration, spotify_url, download_url
    title = r.get("name") or "Unknown Title"
    artist = r.get("artist") or ""
    cover = r.get("cover") or r.get("cover_small")
    duration_sec = r.get("duration")  # seconds as integer
    spotify_url = r.get("spotify_url")
    download_url_hint = r.get("download_url")  # this usually points to billa get_track endpoint

    # Duration checks similar to previous logic
    if not duration_sec:
        return await mystic.edit_text(lang["song_3"])
    if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
        # previous message used SONG_DOWNLOAD_DURATION and dur_min -> adapt
        dur_min = int(duration_sec / 60)
        return await mystic.edit_text(lang["play_4"].format(SONG_DOWNLOAD_DURATION, dur_min))

    # store mapping so callback can reference compact key
    short_key = uuid.uuid4().hex[:10]
    TRACK_STORE[short_key] = {
        "id": r.get("id"),
        "title": title,
        "artist": artist,
        "cover": cover,
        "duration": duration_sec,
        "spotify_url": spotify_url,
        "download_url_hint": download_url_hint,
    }

    # Build inline keyboard: single audio download button (we no longer support video via yt-dlp)
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(f"Download • {title} - {artist}", callback_data=f"song_download api|{short_key}"),
    )
    kb.row(
        InlineKeyboardButton(lang["CLOSE_BUTTON"], callback_data="close"),
    )

    await mystic.delete()
    await message.reply_photo(
        cover,
        caption=lang["song_4"].format(title),
        reply_markup=InlineKeyboardMarkup(kb),
    )


@app.on_callback_query(filters.regex(r"song_download") & ~BANNED_USERS)
@capture_callback_err
@languageCB
async def song_download_cb(client, cq, lang):
    """
    Handles downloads for both the new API-based flow (prefixed with 'api') and preserves old
    stype semantics for backward compatibility (but we've removed YouTube/yt-dlp paths).
    """
    user_id = cq.from_user.id
    _ignored, req = cq.data.split(None, 1)
    stype_key = req  # format: "<method>|<key_or_format>|<maybe_vidid>" in old code; we use "api|<short_key>"
    parts = stype_key.split("|")
    stype = parts[0]

    # Anti-spam
    spam_count = await get_spam_data(user_id)
    if spam_count and spam_count >= 5:
        await block_user(user_id, 600)
        return await cq.answer(
            "You Are Spamming Now! Blocked for 10 minutes For Using /song or /music command.",
            show_alert=True,
        )
    await add_spam_data(user_id)

    try:
        await cq.answer("Downloading... Please wait...")
    except Exception:
        pass

    mystic = await cq.edit_message_text(lang["song_8"])
    file_path = None
    thumb_path = None

    try:
        if stype == "api":
            # api flow: parts = ["api", "<short_key>"]
            if len(parts) < 2:
                return await mystic.edit_text(lang["song_10"])
            short_key = parts[1]
            track = TRACK_STORE.get(short_key)
            if not track:
                return await mystic.edit_text(lang["song_7"])

            title = re.sub(r"\W+", " ", track["title"])
            artist = track.get("artist")
            duration_sec = track.get("duration")
            cover = track.get("cover")
            spotify_url = track.get("spotify_url")
            download_url_hint = track.get("download_url_hint")

            # Download the cover/thumb to pass to sent audio (and to compute width/height if needed)
            try:
                if cover:
                    async with httpx.AsyncClient(timeout=30) as client:
                        rcover = await client.get(cover)
                        if rcover.status_code == 200:
                            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                            tf.write(rcover.content)
                            tf.flush()
                            thumb_path = tf.name
            except Exception:
                thumb_path = None

            # Now fetch the actual downloadable audio file from Billa get_track endpoint.
            # The API provides download_url_hint like:
            # "https://billa-api.vercel.app/get_track?url=https://open.spotify.com/track/..."
            # We'll call that URL and stream the response to a temporary file.
            if not download_url_hint and spotify_url:
                # fallback: build get_track URL
                download_url_hint = f"{BILLA_API_BASE}/get_track?url={httpx.utils.quote(spotify_url, safe=':/?=&')}"

            if not download_url_hint:
                return await mystic.edit_text(lang["song_10"])

            # stream download
            tmpfd, tmpfname = tempfile.mkstemp(suffix=".mp3")
            os.close(tmpfd)
            file_path = tmpfname

            # Stream with httpx to file
            async with httpx.AsyncClient(timeout=600) as client:
                async with client.stream("GET", download_url_hint) as resp:
                    if resp.status_code != 200:
                        # Try one more: maybe API expects URL-encoded param differently
                        return await mystic.edit_text(lang["song_10"])
                    with open(file_path, "wb") as f:
                        async for chunk in resp.aiter_bytes(chunk_size=65536):
                            if chunk:
                                f.write(chunk)

            if not file_path or not os.path.exists(file_path):
                return await mystic.edit_text(lang["song_10"])

            await mystic.edit_text(lang["song_11"])
            await app.send_chat_action(cq.message.chat.id, ChatAction.UPLOAD_AUDIO)

            # Send to user
            await cq.edit_message_media(
                InputMediaAudio(
                    media=file_path,
                    caption=f"{title}\n\nSource: `{spotify_url}`",
                    thumb=thumb_path,
                    title=title,
                    performer=artist,
                )
            )

            # Dump storage copy
            await app.send_audio(
                SONG_DUMP_ID,
                audio=file_path,
                caption=f"Powered by 🌌 Space Api\nSource: `{spotify_url}`",
                title=title,
                performer=artist,
                duration=duration_sec,
                thumb=thumb_path,
            )

        else:
            # Old yt-dlp/YouTube code path removed: inform user
            return await mystic.edit_text("This bot no longer supports YouTube/yt-dlp downloads. Use plain song queries.")

        # Log command usage
        if await is_on_off("LOG_COMMAND"):
            await app.send_message(
                LOGGER_ID,
                f"#SONG\nUser: {cq.from_user.mention} (`{user_id}`)\n"
                f"Query: `{track.get('spotify_url') if stype == 'api' else 'N/A'}`\nType: `{stype}`\n"
                f"Title: `{title}`",
            )

        # Cleanup after 5 minutes (remove downloaded file)
        async def cleanup(path):
            await asyncio.sleep(300)
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"[CLEANUP] Removed file: {path}")
                except Exception as e:
                    print(f"[CLEANUP] Failed: {e}")

        if file_path:
            asyncio.create_task(cleanup(file_path))

    except Exception as err:
        print(f"[SONG] download/upload error: {err}")
        await mystic.edit_text(lang["song_10"])
    finally:
        try:
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
                print(f"[CLEANUP] Removed thumb: {thumb_path}")
        except Exception:
            pass
