import asyncio
import random
import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS, START_IMG_URL, START_VID
from strings import get_string
from OpusV import app
from OpusV.misc import _boot_
from OpusV.plugins.sudo.sudoers import sudoers_list
from OpusV.utils import bot_sys_stats
from OpusV.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats,
    get_served_users,
    is_banned_user,
    is_on_off,
)
from OpusV.utils.decorators.language import LanguageStart
from OpusV.utils.formatters import get_readable_time
from OpusV.utils.inline import private_panel, start_panel
from OpusV.utils.inline.help import help_keyboard


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_keyboard(_)
            return await message.reply_photo(
                photo=START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(3):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=(
                        f"<pre>{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n"
                        f"<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n"
                        f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}</pre>"
                    ),
                )
            return

        elif name.startswith("inf"):
            m = await message.reply_text("🔎")
            video_id = str(name).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={video_id}"
            try:
                results = VideosSearch(query, limit=1)
                data = (await results.next())["result"][0]

                title = data["title"]
                duration = data["duration"]
                views = data["viewCount"]["short"]
                thumbnail = data["thumbnails"][0]["url"].split("?")[0]
                channellink = data["channel"]["link"]
                channel = data["channel"]["name"]
                link = data["link"]
                published = data["publishedTime"]

                searched_text = _["start_6"].format(
                    title, duration, views, published, channellink, channel, app.mention
                )
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=_["S_B_6"], url=link),
                            InlineKeyboardButton(text=_["S_B_4"], url=config.SUPPORT_CHAT),
                        ]
                    ]
                )
                await m.delete()
                await app.send_video(
                    chat_id=message.chat.id,
                    video=thumbnail,
                    caption=searched_text,
                    reply_markup=key,
                )
                if await is_on_off(3):
                    await app.send_message(
                        chat_id=config.LOGGER_ID,
                        text=(
                            f"<pre>{message.from_user.mention} ᴊᴜsᴛ sᴇᴀʀᴄʜᴇᴅ <b>ᴛʀᴀᴄᴋ ɪɴғᴏ</b>.\n\n"
                            f"<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n"
                            f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}</pre>"
                        ),
                    )
            except Exception as e:
                await m.edit(f"<pre><b>ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ɪɴꜰᴏ</b></pre>")
            return

    out = private_panel(_)

    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    UP, CPU, RAM, DISK = await bot_sys_stats()

    await message.reply(
            text='<b>Hᴇʏ, 🧸</b>\n\n<blockquote><b>I’ᴍ ᴠᴇxᴏ, ʏᴏᴜʀ ᴘᴏᴡᴇʀꜰᴜʟ ᴍᴜꜱɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ. ʙᴜɪʟᴛ ᴛᴏ ʙʀɪɴɢ ᴘᴏᴡᴇʀꜰᴜʟ ꜱᴏᴜɴᴅ, ꜱᴍᴏᴏᴛʜ ᴄᴏɴᴛʀᴏʟꜱ, ᴀɴᴅ ᴀɴ ᴇʟɪᴛᴇ ʟɪꜱᴛᴇɴɪɴɢ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ.</b></blockquote>\n<b><blockquote><a href="https://files.catbox.moe/kkqjjc.mp4">✨</a> ᴡʜᴀᴛ ɪ ᴅᴏ:\n• ᴘʟᴀʏ ʜɪɢʜ-Qᴜᴀʟɪᴛʏ ᴍᴜꜱɪᴄ\n• ꜰᴀꜱᴛ ᴄᴏɴᴛʀᴏʟꜱ & ᴄʟᴇᴀɴ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ\n• ᴄᴏᴏʟ ꜰᴇᴀᴛᴜʀᴇꜱ ꜰᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴠɪʙᴇꜱ</blockquote></b>\n<blockquote><b>📚 ɴᴇᴇᴅ ʜᴇʟᴘ?\nᴛᴀᴘ ʜᴇʟᴘ ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴍʏ ᴄᴏᴍᴍᴀɴᴅꜱ.</b></blockquote>',
            reply_markup=InlineKeyboardMarkup(out),
        )
    if await is_on_off(3):
        await app.send_message(
            chat_id=config.LOGGER_ID,
            text=(
                f"<pre><b>{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
                f"<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n"
                f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}</pre></b>"
            ),
        )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_video(
        video=START_VID,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_video(
                    video=START_VID,
                    caption=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
