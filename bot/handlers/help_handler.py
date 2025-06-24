"""Help command handler."""

from telegram import Update
from telegram.ext import ContextTypes

from .base_handler import BaseHandler

class HelpHandler(BaseHandler):
    """Handler for the /help command."""
    
    def __init__(self, handler_registry=None):
        super().__init__()
        self.handler_registry = handler_registry
    
    @property
    def command_name(self) -> str:
        return "help"
    
    @property
    def description(self) -> str:
        return "Show available commands and their descriptions"
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        # Check authorization
        if not await self.check_authorization(update):
            return
        
        # Build comprehensive help text based on current implementation
        help_text = """📋 *Available Commands:*

*Wallet Management:*
• `/start` - Start the bot and check connection
• `/help` - Show available commands and their descriptions
• `/list` - Show all configured wallets
• `/add "company" "wallet" "address"` - Add new wallet
• `/remove "wallet_name"` - Remove wallet  
• `/check` - Check all wallet balances
• `/check "wallet_name"` - Check specific wallet balance
• `/check "wallet1" "wallet2"` - Check multiple specific wallets

*Examples:*
• `/add "KZP" "KZP WDB2" "TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS"`
• `/remove "KZP WDB2"`
• `/list`
• `/check`
• `/check "KZP 96G1"`
• `/check "KZP 96G1" "KZP WDB2"`

*Notes:*
• All arguments must be in quotes
• TRC20 addresses start with 'T' (34 characters)
• Balance reports sent via scheduled messages at midnight GMT+7
• Only authorized team members can use commands"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
        user_name = update.effective_user.first_name or "User"
        self.logger.info(f"Help command processed for user {user_name}")