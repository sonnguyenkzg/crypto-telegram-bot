"""Start command handler."""

from telegram import Update
from telegram.ext import ContextTypes

from .base_handler import BaseHandler

class StartHandler(BaseHandler):
    """Handler for the /start command."""
    
    @property
    def command_name(self) -> str:
        return "start"
    
    @property
    def description(self) -> str:
        return "Start the bot and check connection"
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        user_name = update.effective_user.first_name or "User"
        user_id = str(update.effective_user.id)
        
        self.logger.info(f"Start command received from user {user_name} (ID: {user_id})")
        
        # Check authorization
        if not await self.check_authorization(update):
            return
        
        welcome_message = f"""🤖 **Crypto Wallet Monitor Bot is running!**

Hello {user_name}! 👋

This bot helps you monitor USDT wallet balances.

Environment: `{self.config.ENVIRONMENT}`
Status: ✅ Connected and Ready

Try /help to see available commands."""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        self.logger.info(f"Welcome message sent to authorized user {user_name}")