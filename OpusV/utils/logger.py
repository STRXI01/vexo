from pyrogram.enums import ParseMode

from OpusV import app
from OpusV.utils.database import is_on_off
from OpusV.misc import SUDOERS
from config import LOGGER_ID


async def play_logs(message, streamtype):
    if await is_on_off(2):
        if message.from_user and message.from_user.id in SUDOERS:
            return

        query_text = ""
        if message.text and len(message.text.split(None, 1)) > 1:
            query_text = message.text.split(None, 1)[1]

        logger_text = f"""
<b>{app.mention} ᴘʟᴀʏ ʟᴏɢs</b>

<b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{message.chat.id}</code>
<b>ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {message.chat.title}
<b>ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.chat.username if message.chat.username else 'N/A'}

<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>
<b>ɴᴀᴍᴇ :</b> {message.from_user.mention}
<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username if message.from_user.username else 'N/A'}

<b>ǫᴜᴇʀʏ :</b> {query_text if query_text else 'N/A'}
<b>sᴛʀᴇᴀᴍᴛʏᴘᴇ :</b> {streamtype}"""

        if message.chat.id != LOGGER_ID:
            try:
                await app.send_message(
                    chat_id=LOGGER_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except:
                pass
        return
