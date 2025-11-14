import os
import httpx
import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from OpusV import app


async def upload_catbox(path: str):
    """Upload file to Catbox.moe with retry logic using httpx."""
    url = "https://catbox.moe/user/api.php"

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                with open(path, "rb") as f:
                    files = {"fileToUpload": (os.path.basename(path), f)}
                    data = {"reqtype": "fileupload"}
                    resp = await client.post(url, data=data, files=files)
                    if resp.status_code == 200 and "catbox.moe" in resp.text:
                        return True, resp.text.strip()
            await asyncio.sleep(1)
        except Exception as e:
            last_error = str(e)
            await asyncio.sleep(2)

    return False, last_error if "last_error" in locals() else "Catbox upload failed after retries."


async def upload_anonfiles(path: str):
    """Upload file to AnonFiles as fallback using httpx."""
    url = "https://api.anonfiles.com/upload"
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            with open(path, "rb") as f:
                files = {"file": (os.path.basename(path), f)}
                resp = await client.post(url, files=files)
                data = resp.json()
                if data.get("status"):
                    file_url = data["data"]["file"]["url"]["full"]
                    return True, file_url
                return False, data.get("error", {}).get("message", "AnonFiles upload failed.")
    except Exception as e:
        return False, str(e)


@app.on_message(filters.command(["tgm", "tgt", "paste"]))
async def telegraph_handler(_, message: Message):
    if not message.reply_to_message or not (
        message.reply_to_message.photo
        or message.reply_to_message.video
        or message.reply_to_message.document
    ):
        return await message.reply_text("📎 Please reply to an image, video, or document to upload.")

    media = message.reply_to_message
    file = media.photo or media.video or media.document

    # Reject files over 100 MB
    if file.file_size > 100 * 1024 * 1024:
        return await message.reply_text("⚠️ File too large. Max allowed size is 100 MB.")

    status = await message.reply("🔄 Downloading your media...")

    local_path = None
    try:
        local_path = await media.download()
        await status.edit("⬆️ Uploading to Catbox...")

        success, result = await upload_catbox(local_path)
        host = "Catbox"

        if not success:
            await status.edit("⚠️ Catbox upload failed. Trying AnonFiles...")
            success, result = await upload_anonfiles(local_path)
            host = "AnonFiles"

        if success:
            await status.edit(
                f"✅ Uploaded successfully to **{host}**!\n\n🔗 {result}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📎 View File", url=result)]]
                ),
                disable_web_page_preview=False,
            )
        else:
            await status.edit(f"🛑 Upload failed:\n`{result}`")

    except Exception as e:
        await status.edit(f"🛑 Failed to process media:\n`{e}`")

    finally:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
