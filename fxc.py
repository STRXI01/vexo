"""
Configuration file for Telegram Auto Forwarder Bot
"""

class Config:
    # Bot credentials (required)
    API_ID: int = 27696582  # Replace with your actual API ID
    API_HASH: str = "45fccefb72a57ff1b858339774b6d005"
    BOT_TOKEN: str = "8181624230:AAHWgN-HzgqHq643CejNtuqo_dg4dgQqYok"
    
    # Target channel/group (required)
    TARGET_CHAT_ID: str = "@BillaNothing"  # Can be a group/channel ID
    
    # Directories
    DOWNLOADS_DIR: str = "./downloads"
    CACHE_FILE: str = "./ffiles.json"
    
    # Default settings
    DEFAULT_INTERVAL: int = 10  # seconds
    MAX_RETRY_ATTEMPTS: int = 2
    
    # Authorized users (as list of integers)
    AUTHORIZED_USERS: list = [5960968099, 6115406735]  # Replace with actual user IDs
    
    # File size limits (in MB)
    MAX_FILE_SIZE_MB: int = 2048
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = [
            cls.API_ID, cls.API_HASH, cls.BOT_TOKEN, 
            cls.TARGET_CHAT_ID, cls.AUTHORIZED_USERS
        ]
        return all(field for field in required_fields)
