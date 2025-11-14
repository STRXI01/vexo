"""
Main entry point for Telegram Auto Forwarder Bot
"""
import asyncio
import logging
import sys
from pathlib import Path

from bot_handler import TelegramBot
from fxc import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function"""
    try:
        # Validate configuration
        if not Config.validate():
            logger.error(
                "❌ Invalid configuration!\n"
                "Please set the following environment variables:\n"
                "- API_ID: Your Telegram API ID\n"
                "- API_HASH: Your Telegram API Hash\n"
                "- BOT_TOKEN: Your Bot Token from @BotFather\n"
                "- TARGET_CHAT_ID: Target channel/group ID or Username(e.g., -1001234567890)\n"
                "- AUTHORIZED_USERS: Comma-separated user IDs (e.g., 123456789,987654321)"
            )
            return
        
        # Create bot instance and run
        bot = TelegramBot()
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    # Ensure Python 3.8+
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required!")
        sys.exit(1)
    
    # Run the bot
    asyncio.run(main())
