#!/usr/bin/env python3
# telegram_listener.py
"""
Telegram bot listener for USDT wallet commands.
Handles real-time command processing and user authorization.
"""
import logging
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

from bot.telegram_config import (
    TELEGRAM_BOT_TOKEN, 
    TELEGRAM_CHAT_ID, 
    ALLOWED_TELEGRAM_USERS,
    BOT_USERNAME
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Valid commands
VALID_COMMANDS = ['help', 'check', 'add', 'remove', 'list']


class USDTWalletTelegramBot:
    def __init__(self):
        """Initialize the Telegram bot."""
        self.application = None
        self.bot_username = BOT_USERNAME
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        
        if not self.is_authorized_user(user_id):
            await update.message.reply_text(
                "⛔ You are not authorized to use this bot.\n"
                "Please contact an administrator for access."
            )
            return
        
        welcome_message = (
            "🤖 USDT Wallet Monitor Bot\n\n"
            "I help you monitor USDT TRC20 wallet balances.\n\n"
            "Available Commands:\n"
            "/help - Show all commands\n"
            "/check - Check all wallet balances\n"
            "/check wallet_name - Check specific wallet\n"
            "/list - List all configured wallets\n"
            "/add \"Company\" \"Wallet\" \"Address\" - Add new wallet\n"
            "/remove \"Wallet Name\" - Remove wallet\n\n"
            "✅ You are authorized to use all commands."
        )
        
        await update.message.reply_text(welcome_message)
        
        logger.info(f"✅ /start command processed for authorized user {user_id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        user_id = update.effective_user.id
        
        if not self.is_authorized_user(user_id):
            await update.message.reply_text(
                "⛔ You are not authorized to use this bot."
            )
            return
        
        help_text = (
            "🤖 *USDT Wallet Monitor - Help*\n\n"
            "*📊 Balance Commands:*\n"
            "`/check` - Check all wallet balances\n"
            "`/check \"Wallet Name\"` - Check specific wallet\n\n"
            "*📋 Management Commands:*\n"
            "`/list` - List all configured wallets\n"
            "`/add \"Company\" \"Wallet\" \"Address\"` - Add new wallet\n"
            "`/remove \"Wallet Name\"` - Remove wallet\n\n"
            "*📝 Examples:*\n"
            "`/add \"KZP\" \"Store1\" \"TNZkbytSMdaRJ79CYzv8BGK6LWNmQxcuM8\"`\n"
            "`/check \"KZP Store1\"`\n"
            "`/remove \"KZP Store1\"`\n\n"
            "*ℹ️ Notes:*\n"
            "• Only USDT TRC20 wallets are supported\n"
            "• Wallet addresses must start with 'T'\n"
            "• Use quotes around names with spaces\n"
            "• Balance checks may take a few seconds"
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"✅ /help command processed for user {user_id}")
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command with real functionality."""
        user_id = update.effective_user.id
        
        if not self.is_authorized_user(user_id):
            await update.message.reply_text(
                "⛔ You are not authorized to use this command."
            )
            return
        
        # Get command arguments and join them back to original format
        text = ""
        if context.args:
            text = " ".join(context.args)
        
        try:
            # Import the command handler
            from bot.telegram_commands import handle_telegram_command
            
            # Process the command
            response = handle_telegram_command("check", text, user_id, update.effective_chat.id)
            
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info(f"✅ /check command processed for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in /check command: {e}")
            await update.message.reply_text(
                "❌ Error checking wallet balances. Please try again."
            )
    
    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command with real functionality."""
        user_id = update.effective_user.id
        
        if not self.is_authorized_user(user_id):
            await update.message.reply_text(
                "⛔ You are not authorized to use this command."
            )
            return
        
        # Get command arguments and join them back to original format
        text = ""
        if context.args:
            text = " ".join(context.args)
        
        try:
            # Import the command handler
            from bot.telegram_commands import handle_telegram_command
            
            # Process the command
            response = handle_telegram_command("add", text, user_id, update.effective_chat.id)
            
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info(f"✅ /add command processed for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in /add command: {e}")
            await update.message.reply_text(
                "❌ Error adding wallet. Please try again."
            )
    
    async def remove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove command with real functionality."""
        user_id = update.effective_user.id
        
        if not self.is_authorized_user(user_id):
            await update.message.reply_text(
                "⛔ You are not authorized to use this command."
            )
            return
        
        # Get command arguments and join them back to original format
        text = ""
        if context.args:
            text = " ".join(context.args)
        
        try:
            # Import the command handler
            from bot.telegram_commands import handle_telegram_command
            
            # Process the command
            response = handle_telegram_command("remove", text, user_id, update.effective_chat.id)
            
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info(f"✅ /remove command processed for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in /remove command: {e}")
            await update.message.reply_text(
                "❌ Error removing wallet. Please try again."
            )
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command with real functionality."""
        user_id = update.effective_user.id
        
        if not self.is_authorized_user(user_id):
            await update.message.reply_text(
                "⛔ You are not authorized to use this command."
            )
            return
        
        try:
            # Import the command handler
            from bot.telegram_commands import handle_telegram_command
            
            # Process the command
            response = handle_telegram_command("list", "", user_id, update.effective_chat.id)
            
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info(f"✅ /list command processed for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in /list command: {e}")
            await update.message.reply_text(
                "❌ Error listing wallets. Please try again."
            )
    
    async def unauthorized_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages from unauthorized users."""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.warning(f"⛔ Unauthorized access attempt by user {user_id} (@{username})")
        
        await update.message.reply_text(
            "⛔ You are not authorized to use this bot.\n"
            "Please contact an administrator for access.\n\n"
            f"Your User ID: `{user_id}`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands."""
        user_id = update.effective_user.id
        
        if not self.is_authorized_user(user_id):
            await self.unauthorized_command(update, context)
            return
        
        await update.message.reply_text(
            "❓ Unknown command. Use /help to see available commands.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"❓ Unknown command from user {user_id}")
    
    def is_authorized_user(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot."""
        return user_id in ALLOWED_TELEGRAM_USERS
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f"❌ Error occurred: {context.error}")
        
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again."
            )
    
    def setup_handlers(self):
        """Set up command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("check", self.check_command))
        self.application.add_handler(CommandHandler("add", self.add_command))
        self.application.add_handler(CommandHandler("remove", self.remove_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        
        # Handle all other messages (for unauthorized users)
        self.application.add_handler(
            MessageHandler(filters.ALL, self.unknown_command)
        )
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    def start(self):
        """Start the Telegram bot."""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        
        if not TELEGRAM_CHAT_ID:
            logger.error("❌ TELEGRAM_CHAT_ID not found in environment variables")
            return
        
        # Create application
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Setup handlers
        self.setup_handlers()
        
        logger.info("🚀 Starting USDT Wallet Telegram Bot...")
        logger.info(f"📡 Monitoring chat: {TELEGRAM_CHAT_ID}")
        logger.info(f"🔐 Authorized users: {ALLOWED_TELEGRAM_USERS}")
        logger.info("💬 Available commands:")
        logger.info("   /start    - Bot introduction")
        logger.info("   /help     - Show all commands")
        logger.info("   /check    - Check wallet balances")
        logger.info("   /add      - Add new wallet")
        logger.info("   /remove   - Remove wallet")
        logger.info("   /list     - List wallets")
        logger.info("")
        logger.info("🔄 Bot running... Press Ctrl+C to stop")
        
        try:
            # Start polling
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")


def main():
    """Main entry point."""
    bot = USDTWalletTelegramBot()
    bot.start()


if __name__ == "__main__":
    main()