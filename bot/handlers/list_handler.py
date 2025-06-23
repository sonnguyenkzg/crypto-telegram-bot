"""List command handler."""

from telegram import Update
from telegram.ext import ContextTypes

from .base_handler import BaseHandler
from bot.services.wallet_service import WalletService

class ListHandler(BaseHandler):
    """Handler for the /list command."""
    
    def __init__(self):
        super().__init__()
        self.wallet_service = WalletService()
    
    @property
    def command_name(self) -> str:
        return "list"
    
    @property
    def description(self) -> str:
        return "Show all configured wallets"
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /list command."""
        user_name = update.effective_user.first_name or "User"
        user_id = str(update.effective_user.id)
        
        self.logger.info(f"List command received from user {user_name} (ID: {user_id})")
        
        # Check authorization
        if not await self.check_authorization(update):
            return
        
        # Get wallet list from service
        success, message = self.wallet_service.list_wallets()
        
        # Send response
        await update.message.reply_text(message, parse_mode='Markdown')
        
        self.logger.info(f"List command processed for user {user_name}, {message.count('•')} wallets shown")