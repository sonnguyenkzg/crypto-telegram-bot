#!/usr/bin/env python3
"""
Telegram Crypto Wallet Monitor Bot - Phase 1: Basic Setup
Migration from Slack to Telegram
"""

import os
import logging
import asyncio
from typing import List, Set
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
from dotenv import load_dotenv

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

class TelegramCryptoBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.target_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.authorized_users = self._load_authorized_users()
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Initialize application
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _load_authorized_users(self) -> Set[int]:
        """Load authorized user IDs from environment"""
        auth_users = os.getenv('AUTHORIZED_USERS', '')
        if not auth_users:
            logger.warning("No AUTHORIZED_USERS set - bot will accept all users!")
            return set()
        
        try:
            return {int(user_id.strip()) for user_id in auth_users.split(',')}
        except ValueError as e:
            logger.error(f"Invalid AUTHORIZED_USERS format: {e}")
            return set()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("check", self.check_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("add", self.add_command))
        self.application.add_handler(CommandHandler("remove", self.remove_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Message handler for non-commands (debugging)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        if not self.authorized_users:  # If no users set, allow all (setup mode)
            return True
        return user_id in self.authorized_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Start command from user {user.id} ({user.username}) in chat {chat.id}")
        
        if not await self.is_authorized(user.id):
            await update.message.reply_text(
                "❌ Access denied. You are not authorized to use this bot."
            )
            return
        
        welcome_message = f"""
🤖 **Crypto Wallet Monitor Bot**

Welcome {user.first_name}! This bot monitors USDT TRC20 wallet balances.

**Available Commands:**
/help - Show all commands
/check - Check wallet balances
/list - List all wallets
/add - Add new wallet
/remove - Remove wallet
/status - Bot status

**Chat Info:**
- Chat ID: `{chat.id}`
- User ID: `{user.id}`
- Username: @{user.username or 'N/A'}
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        help_text = """
📋 **Available Commands:**

**Balance Commands:**
/check - Check all wallet balances
/check WalletName - Check specific wallet
/list - Show all configured wallets

**Management Commands:**
/add Company WalletName Address - Add new wallet
/remove WalletName - Remove wallet

**Info Commands:**
/help - Show this help
/status - Bot status and info

**Examples:**
`/add KZP MainStore TNZkbytSMdaRJ79CYzv8BGK6LWNmQxcuM8`
`/check MainStore`
`/remove MainStore`

**Note:** Only TRC20 USDT wallets are supported.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command - placeholder for Phase 3"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        # Placeholder - will be implemented in Phase 3
        wallet_name = ' '.join(context.args) if context.args else None
        
        if wallet_name:
            message = f"🔍 Checking balance for wallet: {wallet_name}\n\n⚠️ Feature coming in Phase 3!"
        else:
            message = "🔍 Checking all wallet balances...\n\n⚠️ Feature coming in Phase 3!"
        
        await update.message.reply_text(message)
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command - placeholder for Phase 3"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        await update.message.reply_text("📋 Listing all wallets...\n\n⚠️ Feature coming in Phase 3!")
    
    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command - placeholder for Phase 3"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ Usage: `/add Company WalletName Address`\n\n"
                "Example: `/add KZP MainStore TNZkbytSMdaRJ79CYzv8BGK6LWNmQxcuM8`",
                parse_mode='Markdown'
            )
            return
        
        company, wallet_name, address = context.args[0], context.args[1], context.args[2]
        await update.message.reply_text(
            f"➕ Adding wallet:\n"
            f"Company: {company}\n"
            f"Name: {wallet_name}\n"
            f"Address: {address}\n\n"
            f"⚠️ Feature coming in Phase 3!"
        )
    
    async def remove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove command - placeholder for Phase 3"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/remove WalletName`\n\n"
                "Example: `/remove MainStore`",
                parse_mode='Markdown'
            )
            return
        
        wallet_name = ' '.join(context.args)
        await update.message.reply_text(
            f"🗑️ Removing wallet: {wallet_name}\n\n⚠️ Feature coming in Phase 3!"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        bot_info = await context.bot.get_me()
        chat = update.effective_chat
        
        status_message = f"""
🤖 **Bot Status**

**Bot Info:**
- Name: {bot_info.first_name}
- Username: @{bot_info.username}
- ID: {bot_info.id}

**Current Chat:**
- Chat ID: `{chat.id}`
- Chat Type: {chat.type}
- Title: {chat.title or 'N/A'}

**Authorization:**
- Authorized Users: {len(self.authorized_users) if self.authorized_users else 'All users (setup mode)'}
- Your Access: ✅ Authorized

**Phase Status:**
- Phase 1: ✅ Complete (Setup & Auth)
- Phase 2: ⚠️ In Progress (Commands)
- Phase 3: ⏳ Pending (Core Features)
- Phase 4: ⏳ Pending (Telegram Adaptations)
- Phase 5: ⏳ Pending (Deployment)
        """
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages (for debugging)"""
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Message from user {user.id} in chat {chat.id}: {update.message.text}")
        
        # Only respond if authorized (to avoid spam)
        if await self.is_authorized(user.id):
            await update.message.reply_text(
                "ℹ️ I only respond to commands. Type /help to see available commands."
            )
    
    async def send_daily_report(self, message: str):
        """Send daily report to configured chat (placeholder for Phase 3)"""
        if not self.target_chat_id:
            logger.error("TELEGRAM_CHAT_ID not configured")
            return
        
        try:
            await self.application.bot.send_message(
                chat_id=self.target_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("Daily report sent successfully")
        except Exception as e:
            logger.error(f"Failed to send daily report: {e}")
    
    async def setup_bot_commands(self):
        """Set up bot commands for Telegram UI"""
        commands = [
            BotCommand("start", "Start the bot and show welcome message"),
            BotCommand("help", "Show all available commands"),
            BotCommand("check", "Check wallet balances"),
            BotCommand("list", "List all configured wallets"),
            BotCommand("add", "Add a new wallet"),
            BotCommand("remove", "Remove a wallet"),
            BotCommand("status", "Show bot status"),
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands set up successfully")
    
    async def run(self):
        """Start the bot"""
        logger.info("Starting Telegram Crypto Bot...")
        
        # Set up bot commands
        await self.setup_bot_commands()
        
        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot is running! Press Ctrl+C to stop.")
        
        # Keep the bot running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

def main():
    """Main function"""
    try:
        bot = TelegramCryptoBot()
        asyncio.run(bot.run())
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()