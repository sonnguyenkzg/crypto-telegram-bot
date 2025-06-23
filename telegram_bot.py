#!/usr/bin/env python3
"""
Telegram Crypto Wallet Monitor Bot - Step 4: Add Wallet Functionality
Added wallet creation with strict quoted argument parsing.
"""

import logging
from telegram import Update
from telegram.ext import Application

from bot.utils.config import Config
from bot.utils.handler_registry import HandlerRegistry
from bot.handlers import StartHandler, HelpHandler, ListHandler, AddHandler

# Setup logging and configuration
logger = Config.setup_logging()

def setup_handlers() -> HandlerRegistry:
    """Setup and register all command handlers."""
    registry = HandlerRegistry()
    
    # Register handlers
    start_handler = StartHandler()
    help_handler = HelpHandler(handler_registry=registry)
    list_handler = ListHandler()
    add_handler = AddHandler()
    
    registry.register_handler(start_handler)
    registry.register_handler(help_handler)
    registry.register_handler(list_handler)
    registry.register_handler(add_handler)
    
    return registry

def main() -> None:
    """Main function to run the bot."""
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Setup handlers
        handler_registry = setup_handlers()
        logger.info("Command handlers setup completed")
        
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Register all handlers with the application
        handler_registry.register_with_application(application)
        
        # Log startup information
        logger.info(f"Environment: {Config.ENVIRONMENT}")
        logger.info(f"Authorized users: {len(Config.get_authorized_users())}")
        logger.info(f"Registered commands: {', '.join(handler_registry.list_commands())}")
        logger.info("Starting Telegram bot...")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()