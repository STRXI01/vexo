import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from config import BANNED_USERS
from OpusV.core.call import Space
from OpusV.utils.admin_filters import admin_filter
from OpusV.utils.database import group_assistant
from OpusV import app

VC_CACHE = {}
VC_TRACKING_ENABLED = set()
VC_MONITOR_TASKS = {}

async def monitor_vc_changes(chat_id: int):
    """Background task to monitor voice chat changes."""
    try:
        assistant = await group_assistant(Space, chat_id)
        if not assistant:
            raise Exception("Assistant not found or not initialized.")

        # Initial log of current VC members
        participants = await assistant.get_participants(chat_id)
        current_ids = set()
        joined_lines = []

        if participants:
            for p in participants:
                current_ids.add(p.user_id)
                try:
                    user = await app.get_users(p.user_id)
                    name = user.mention if user else f"<code>{p.user_id}</code>"
                except Exception:
                    name = f"<code>{p.user_id}</code>"

                status = ["Muted" if p.muted else "Unmuted"]
                if getattr(p, "screen_sharing", False):
                    status.append("Screen Sharing")

                vol = getattr(p, "volume", None)
                if vol:
                    status.append(f"Volume: {vol}")

                joined_lines.append(f"#InVC\n<b>Name:</b> {name}\n<b>Status:</b> {', '.join(status)}")

            if joined_lines:
                result = "\n\n".join(joined_lines)
                result += f"\n\n👥 <b>Now in VC:</b> {len(participants)}"
                try:
                    msg = await app.send_message(chat_id, result)
                    await asyncio.sleep(30)
                    await msg.delete()
                except Exception:
                    pass

        VC_CACHE[chat_id] = current_ids

        # Begin monitoring loop
        while chat_id in VC_TRACKING_ENABLED:
            await asyncio.sleep(5)

            assistant = await group_assistant(Space, chat_id)
            if not assistant:
                raise Exception("Assistant not found or not initialized.")
            try:
                participants = await assistant.get_participants(chat_id)
            except Exception as e:
                raise Exception(f"Could not fetch participants: {e}")

            current_ids = set(p.user_id for p in participants)
            old_ids = VC_CACHE.get(chat_id, set())
            VC_CACHE[chat_id] = current_ids

            joined_lines = []
            left_lines = []

            for user_id in current_ids - old_ids:
                try:
                    user = await app.get_users(user_id)
                    name = user.mention if user else f"<code>{user_id}</code>"
                except Exception:
                    name = f"<code>{user_id}</code>"
                joined_lines.append(f"#JoinedVC\n<b>Name:</b> {name}")

            for user_id in old_ids - current_ids:
                try:
                    user = await app.get_users(user_id)
                    name = user.mention if user else f"<code>{user_id}</code>"
                except Exception:
                    name = f"<code>{user_id}</code>"
                left_lines.append(f"#LeftVC\n<b>Name:</b> {name}")

            if joined_lines or left_lines:
                result = "\n\n".join(joined_lines + left_lines)
                result += f"\n\n👥 <b>Now in VC:</b> {len(current_ids)}"
                try:
                    msg = await app.send_message(chat_id, result)
                    await asyncio.sleep(30)
                    await msg.delete()
                except FloodWait as fw:
                    await asyncio.sleep(fw.value)
                    msg = await app.send_message(chat_id, result)
                    await asyncio.sleep(30)
                    await msg.delete()
                except Exception:
                    pass

    except Exception as e:
        try:
            await app.send_message(chat_id, f"❌ VC monitoring stopped due to error: {e}")
        except Exception:
            pass
        VC_TRACKING_ENABLED.discard(chat_id)
        VC_CACHE.pop(chat_id, None)
        VC_MONITOR_TASKS.pop(chat_id, None)


@app.on_message(filters.command(["vcinfo", "infovc", "vclogger"]) & filters.group & admin_filter & ~BANNED_USERS)
async def vc_info(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(None, 1)

    if len(args) == 2 and args[1].lower() in ["on", "enable"]:
        if chat_id not in VC_TRACKING_ENABLED:
            VC_TRACKING_ENABLED.add(chat_id)
            task = asyncio.create_task(monitor_vc_changes(chat_id))
            VC_MONITOR_TASKS[chat_id] = task
            return await message.reply_text("✅ VC tracking enabled for this group. Now I'll track & notify #JoinedVC and #LeftVC users.")
        return await message.reply_text("✅ VC tracking is already enabled.")

    elif len(args) == 2 and args[1].lower() in ["off", "disable"]:
        if chat_id in VC_TRACKING_ENABLED:
            VC_TRACKING_ENABLED.discard(chat_id)
            VC_CACHE.pop(chat_id, None)
            if chat_id in VC_MONITOR_TASKS:
                VC_MONITOR_TASKS[chat_id].cancel()
                VC_MONITOR_TASKS.pop(chat_id, None)
            return await message.reply_text("❌ VC tracking disabled and cache cleared.")
        return await message.reply_text("❌ VC tracking is already disabled.")

    try:
        assistant = await group_assistant(Space, chat_id)
        if not assistant:
            return await message.reply_text("❌ Assistant not found. Make sure it has joined the VC.")
        participants = await assistant.get_participants(chat_id)

        if not participants:
            if chat_id not in VC_TRACKING_ENABLED:
                return await message.reply_text("❌ No users found in the voice chat.")
            else:
                VC_CACHE[chat_id] = set()
                return

        current_ids = set()
        joined_lines = []

        for p in participants:
            user_id = p.user_id
            current_ids.add(user_id)

            if chat_id not in VC_TRACKING_ENABLED:
                try:
                    user = await app.get_users(user_id)
                    name = user.mention if user else f"<code>{user_id}</code>"
                except Exception:
                    name = f"<code>{user_id}</code>"

                status = ["Muted" if p.muted else "Unmuted"]
                if getattr(p, "screen_sharing", False):
                    status.append("Screen Sharing")

                vol = getattr(p, "volume", None)
                if vol:
                    status.append(f"Volume: {vol}")

                joined_lines.append(f"#InVC\n<b>Name:</b> {name}\n<b>Status:</b> {', '.join(status)}")

        if joined_lines:
            result = "\n\n".join(joined_lines)
            result += f"\n\n👥 <b>Total in VC:</b> {len(participants)}"
            await message.reply_text(result)

    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        return await vc_info(client, message)
    except Exception as e:
        await message.reply_text(f"❌ Failed to fetch VC info.\n<b>Error:</b> {e}")