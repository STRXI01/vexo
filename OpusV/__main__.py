import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from OpusV import LOGGER, app, userbot
from OpusV.core.call import Space
from OpusV.misc import sudo
from OpusV.plugins import ALL_MODULES
from OpusV.utils.database import get_banned_users, get_gbanned
from OpusV.utils.cookie_handler import fetch_and_store_cookies 
from config import BANNED_USERS

from OpusV.antispam import (
    init_antispam,
    antispam_filter,
    global_antispam_handler,
)

from pyrogram.handlers import MessageHandler


async def load_banned_users():
    """Load banned users from database avoiding duplicates"""
    try:
        # Load globally banned users
        gbanned_users = await get_gbanned()
        if gbanned_users:
            for user_id in gbanned_users:
                BANNED_USERS.add(user_id)
            LOGGER("OpusV").info(f"🚫 Loaded {len(gbanned_users)} globally banned users")
        
        # Load other banned users (if different from gbanned)
        banned_users = await get_banned_users()
        if banned_users:
            new_bans = 0
            for user_id in banned_users:
                if user_id not in BANNED_USERS:
                    BANNED_USERS.add(user_id)
                    new_bans += 1
            if new_bans > 0:
                LOGGER("OpusV").info(f"🚫 Loaded {new_bans} additional banned users")
        
        total_banned = len(BANNED_USERS)
        if total_banned > 0:
            LOGGER("OpusV").info(f"🛡️ Total banned users in memory: {total_banned}")
        
    except Exception as e:
        LOGGER("OpusV").error(f"⚠️ Failed to load banned users: {e}")


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("⚠️ Activation Failed - Assistant sessions are missing.")
        exit()

    try:
        await fetch_and_store_cookies()
        LOGGER("OpusV").info("🍪 Cookies Integrated - Y-t music stream ready.")
    except Exception as e:
        LOGGER("OpusV").warning(f"☁️ Cookie Warning - {e}")

    # Load sudo users
    await sudo()

    # Load banned users with improved handling
    await load_banned_users()

    # Start the app
    try:
        await app.start()
        LOGGER("OpusV").info("🚀 Bot client started successfully")
    except Exception as e:
        LOGGER("OpusV").error(f"❌ Failed to start bot client: {e}")
        exit()

    # Initialize antispam system
    try:
        init_antispam()
        app.add_handler(MessageHandler(global_antispam_handler, antispam_filter()))
        LOGGER("OpusV").info("🛡️ Shields Up - Anti-Spam active.")
    except Exception as e:
        LOGGER("OpusV").error(f"⚠️ Failed to initialize antispam: {e}")

    # Load all plugin modules
    try:
        for all_module in ALL_MODULES:
            importlib.import_module("OpusV.plugins" + all_module)
        LOGGER("OpusV.plugins").info("🧩 Module Constellation - All systems synced.")
    except Exception as e:
        LOGGER("OpusV").error(f"❌ Failed to load plugins: {e}")
        exit()

    # Start userbot
    try:
        await userbot.start()
        LOGGER("OpusV").info("👤 Userbot started successfully")
    except Exception as e:
        LOGGER("OpusV").error(f"⚠️ Userbot start failed: {e}")

    # Start voice chat system
    try:
        await Space.start()
        LOGGER("OpusV").info("🎵 Voice system initialized")
    except Exception as e:
        LOGGER("OpusV").error(f"⚠️ Voice system failed: {e}")

    # Test voice chat connection
    try:
        await Space.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
        LOGGER("OpusV").info("📡 Voice stream test successful")
    except NoActiveGroupCall:
        LOGGER("OpusV").error(
            "🔇 No Active VC - Log Group voice chat is dormant.\n"
            "💀 Aborting Opus Launch..."
        )
        exit()
    except Exception as e:
        LOGGER("OpusV").warning(f"📡 Voice stream test warning: {e}")

    # Finalize setup
    try:
        await Space.decorators()
        LOGGER("OpusV").info(
            "⚡ Storm Online - Opus music sequence activated.\n"
            "☁️ Part of Storm Servers × Opus Project."
        )
    except Exception as e:
        LOGGER("OpusV").error(f"⚠️ Space decorators failed: {e}")

    # Keep the bot running
    try:
        await idle()
    except KeyboardInterrupt:
        LOGGER("OpusV").info("🛑 Received stop signal")
    except Exception as e:
        LOGGER("OpusV").error(f"⚠️ Idle loop error: {e}")
    finally:
        # Cleanup
        try:
            await app.stop()
            LOGGER("OpusV").info("🤖 Bot client stopped")
        except:
            pass
        
        try:
            await userbot.stop()
            LOGGER("OpusV").info("👤 Userbot stopped")
        except:
            pass
        
        LOGGER("OpusV").info("🌩️ Cycle Closed - Opus sleeps under the storm.")


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(init())
    except KeyboardInterrupt:
        LOGGER("OpusV").info("🛑 Bot stopped by user")
    except Exception as e:
        LOGGER("OpusV").error(f"💥 Critical error: {e}")
