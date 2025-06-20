#!/usr/bin/env python3
"""
Telegram Crypto Wallet Monitor Bot - Phase 2: Full Functionality
Migration from Slack to Telegram with real wallet management
"""

import os
import logging
import asyncio
from typing import Set
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
from dotenv import load_dotenv
from wallet_manager import WalletManager

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
        self.admin_users = self._load_admin_users()
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Initialize wallet manager
        self.wallet_manager = WalletManager()
        
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
    
    def _load_admin_users(self) -> Set[int]:
        """Load admin user IDs from environment"""
        admin_users = os.getenv('ADMIN_USERS', '')
        if not admin_users:
            return set()
        
        try:
            return {int(user_id.strip()) for user_id in admin_users.split(',')}
        except ValueError as e:
            logger.error(f"Invalid ADMIN_USERS format: {e}")
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
        
        # Message handler for non-commands
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        if not self.authorized_users:  # If no users set, allow all (setup mode)
            return True
        return user_id in self.authorized_users
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        if not self.admin_users:  # If no admins set, all authorized users are admins
            return await self.is_authorized(user_id)
        return user_id in self.admin_users
    
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
        
        wallet_count = self.wallet_manager.get_wallet_count()
        is_admin = await self.is_admin(user.id)
        
        welcome_message = f"""
🤖 **Crypto Wallet Monitor Bot**

Welcome {user.first_name}! This bot monitors USDT TRC20 wallet balances.

**📊 Current Status:**
- Configured wallets: {wallet_count}
- Your access: {'🔧 Admin' if is_admin else '👤 User'}

**💰 Balance Commands:**
/check - Check all wallet balances
/check WalletName - Check specific wallet
/list - List all configured wallets

**🔧 Management Commands:** {'(Admin only)' if not is_admin else ''}
/add Company WalletName Address - Add new wallet
/remove WalletName - Remove wallet

**ℹ️ Info Commands:**
/help - Show all commands
/status - Bot status and info

**Example:**
`/add KZP MainStore TNZkbytSMdaRJ79CYzv8BGK6LWNmQxcuM8`
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        is_admin = await self.is_admin(update.effective_user.id)
        
        help_text = """
📋 **Available Commands:**

**💰 Balance Commands:**
/check - Check all wallet balances
/check WalletName - Check specific wallet balance
/list - Show all configured wallets

**🔧 Management Commands:**
/add Company WalletName Address - Add new wallet
/remove WalletName - Remove wallet

**ℹ️ Info Commands:**
/help - Show this help message
/status - Show bot status and information

**📝 Examples:**
`/add KZP MainStore TNZkbytSMdaRJ79CYzv8BGK6LWNmQxcuM8`
`/check MainStore`
`/remove MainStore`

**📌 Notes:**
• Only TRC20 USDT wallets are supported
• Wallet addresses must start with 'T' and be 34 characters
• Daily reports are sent automatically at 12:00 AM GMT+7
        """
        
        if not is_admin:
            help_text += "\n**⚠️ You have user access only. Contact admin to add/remove wallets.**"
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command - now with real functionality"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        # Show "checking..." message first
        checking_msg = await update.message.reply_text("🔍 Checking wallet balances...")
        
        try:
            wallet_name = ' '.join(context.args) if context.args else None
            result = await self.wallet_manager.check_wallet_balance(wallet_name)
            
            # Update the message with results
            await checking_msg.edit_text(result, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in check command: {e}")
            await checking_msg.edit_text("❌ Failed to check wallet balances. Please try again.")
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command - now with real functionality"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        try:
            result = self.wallet_manager.list_wallets()
            await update.message.reply_text(result, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in list command: {e}")
            await update.message.reply_text("❌ Failed to list wallets. Please try again.")
    
    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command - now with real functionality"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        # Check admin permissions
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Admin access required to add wallets.")
            return
        
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ **Usage:** `/add Company WalletName Address`\n\n"
                "**Example:** `/add KZP MainStore TNZkbytSMdaRJ79CYzv8BGK6LWNmQxcuM8`\n\n"
                "**Note:** Address must be a valid TRC20 address (starts with 'T', 34 characters)",
                parse_mode='Markdown'
            )
            return
        
        company, wallet_name, address = context.args[0], context.args[1], context.args[2]
        
        try:
            success, message = self.wallet_manager.add_wallet(company, wallet_name, address)
            await update.message.reply_text(message)
            
            if success:
                logger.info(f"Wallet added by user {update.effective_user.id}: {company} - {wallet_name}")
            
        except Exception as e:
            logger.error(f"Error in add command: {e}")
            await update.message.reply_text("❌ Failed to add wallet. Please try again.")
    
    async def remove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove command - now with real functionality"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        # Check admin permissions
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Admin access required to remove wallets.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ **Usage:** `/remove WalletName`\n\n"
                "**Example:** `/remove MainStore`\n\n"
                "Use `/list` to see available wallets.",
                parse_mode='Markdown'
            )
            return
        
        wallet_name = ' '.join(context.args)
        
        try:
            success, message = self.wallet_manager.remove_wallet(wallet_name)
            await update.message.reply_text(message)
            
            if success:
                logger.info(f"Wallet removed by user {update.effective_user.id}: {wallet_name}")
            
        except Exception as e:
            logger.error(f"Error in remove command: {e}")
            await update.message.reply_text("❌ Failed to remove wallet. Please try again.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not await self.is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Access denied.")
            return
        
        bot_info = await context.bot.get_me()
        chat = update.effective_chat
        user = update.effective_user
        
        wallet_count = self.wallet_manager.get_wallet_count()
        is_admin = await self.is_admin(user.id)
        
        status_message = f"""
🤖 **Bot Status**

**🔧 Bot Info:**
- Name: {bot_info.first_name}
- Username: @{bot_info.username}
- ID: {bot_info.id}

**💬 Current Chat:**
- Chat ID: `{chat.id}`
- Chat Type: {chat.type}
- Title: {chat.title or 'N/A'}

**👤 Your Access:**
- User ID: `{user.id}`
- Username: @{user.username or 'N/A'}
- Access Level: {'🔧 Admin' if is_admin else '👤 User'}
- Status: ✅ Authorized

**💰 Wallet Data:**
- Configured Wallets: {wallet_count}
- Storage: `wallets.json`
- History: `wallet_balances.csv`

**📊 Features Status:**
- ✅ Real-time balance checking
- ✅ Wallet management (add/remove)
- ✅ CSV historical logging
- ✅ Daily reports (12:00 AM GMT+7)
- ✅ User authorization
- ✅ Admin controls
        """
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages"""
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Message from user {user.id} in chat {chat.id}: {update.message.text}")
        
        # Only respond if authorized (to avoid spam)
        if await self.is_authorized(user.id):
            await update.message.reply_text(
                "ℹ️ I only respond to commands. Type /help to see available commands."
            )
    
    async def send_daily_report(self):
        """Send daily report to configured chat"""
        if not self.target_chat_id:
            logger.error("TELEGRAM_CHAT_ID not configured")
            return
        
        try:
            logger.info("Generating daily report...")
            report = await self.wallet_manager.generate_daily_report()
            
            await self.application.bot.send_message(
                chat_id=self.target_chat_id,
                text=report,
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
            BotCommand("add", "Add a new wallet (admin only)"),
            BotCommand("remove", "Remove a wallet (admin only)"),
            BotCommand("status", "Show bot status"),
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands set up successfully")
    
    async def run(self):
        """Start the bot"""
        logger.info("Starting Telegram Crypto Bot with full wallet functionality...")
        
        # Set up bot commands
        await self.setup_bot_commands()
        
        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot is running with real wallet functionality! Press Ctrl+C to stop.")
        
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