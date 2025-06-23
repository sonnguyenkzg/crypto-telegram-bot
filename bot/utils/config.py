"""Configuration management for the Telegram crypto bot."""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for bot settings."""
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Authorization settings
    AUTHORIZED_USER = os.getenv('AUTHORIZED_USER')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEV')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_authorized_users(cls):
        """Get list of authorized users based on environment."""
        if cls.ENVIRONMENT == 'DEV':
            # In DEV, use the AUTHORIZED_USER from .env
            return [cls.AUTHORIZED_USER] if cls.AUTHORIZED_USER else []
        else:
            # In PROD, you can add multiple users or load from file
            return [cls.AUTHORIZED_USER] if cls.AUTHORIZED_USER else []
    
    @classmethod
    def setup_logging(cls):
        """Setup logging configuration."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO),
            handlers=[
                logging.FileHandler('telegram_bot.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        required_vars = ['TELEGRAM_BOT_TOKEN', 'AUTHORIZED_USER']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True