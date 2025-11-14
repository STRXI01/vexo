import asyncio
import random
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.types import Message

import config
from config import autoclean
from strings import get_string
from OpusV import app
from OpusV.misc import SUDOERS
from OpusV.utils.database import (
    get_lang,
    get_served_chats,
    is_suggestion,
    suggestion_on,
    suggestion_off,
)

LEAVE_TIME = config.AUTO_SUGGESTION_TIME

suggestor = {}
strings = [item for item in get_string("en") if item[:3] == "sug" and item != "sug_0"]


@app.on_message(filters.command("suggestions") & filters.group & SUDOERS)
async def toggle_suggestions(_, message: Message):
    if len(message.command) == 1:
        return await message.reply_text("Usage: /suggestions on | off")

    mode = message.command[1].lower()
    if mode == "on":
        await suggestion_on(message.chat.id)
        await message.reply_text("Automatic Songs Recommendations/Suggestions are now turned ON in this chat.")
    elif mode == "off":
        await suggestion_off(message.chat.id)
        await message.reply_text("❌ Auto Songs Suggestions are now turned OFF in this chat.")
    else:
        await message.reply_text("Usage: /suggestions on | off")


async def auto_suggestion_loop():
    if config.AUTO_SUGGESTION_MODE != str(True):
        return

    while not await asyncio.sleep(LEAVE_TIME):
        try:
            chats = []
            schats = await get_served_chats()
            for chat in schats:
                chats.append(int(chat["chat_id"]))
            total = len(chats)
            if total >= 100:
                total //= 10
            send_to = 0
            random.shuffle(chats)
            for x in chats:
                if send_to == total:
                    break
                if x == config.LOG_ERROR_ID:
                    continue
                if not await is_suggestion(x):
                    continue
                try:
                    language = await get_lang(x)
                    _ = get_string(language)
                except Exception:
                    _ = get_string("en")

                string = random.choice(strings)
                if previous := suggestor.get(x):
                    while previous == (string.split("_")[1]):
                        string = random.choice(strings)
                suggestor[x] = string.split("_")[1]

                try:
                    msg = _["sug_0"] + _[string]
                    sent = await app.send_message(x, msg)

                    if x not in clean:
                        clean[x] = []

                    time_now = datetime.now()
                    put = {
                        "msg_id": sent.message_id,
                        "timer_after": time_now + timedelta(minutes=config.CLEANMODE_DELETE_MINS),
                    }
                    clean[x].append(put)
                    send_to += 1
                except Exception:
                    pass
        except Exception:
            pass


asyncio.create_task(auto_suggestion_loop())
