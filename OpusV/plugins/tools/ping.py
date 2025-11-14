from datetime import datetime
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from config import *
from OpusV import app
from OpusV.core.call import Space
from OpusV.utils import bot_sys_stats
from OpusV.utils.decorators.language import language
from OpusV.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL

@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    
    pytgping, stats, response = await asyncio.gather(
        Space.ping(),
        bot_sys_stats(),
        message.reply_text(
            _["ping_1"].format(app.mention),
        )
    )
    
    UP, CPU, RAM, DISK = stats
    resp = (datetime.now() - start).microseconds / 10000
    
    await response.edit_text(
        _["ping_2"].format(resp, app.mention, UP),
        reply_markup=supp_markup(_),
    )
