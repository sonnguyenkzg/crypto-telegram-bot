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
        
        # Build help text dynamically from registered handlers
        help_lines = ["📋 **Available Commands:**\n"]
        
        if self.handler_registry:
            # Get commands from registry
            for handler in self.handler_registry.get_all_handlers():
                help_lines.append(f"/{handler.command_name} - {handler.description}")
        else:
            # Fallback static help (for this step)
            help_lines.extend([
                "/start - Start the bot and check connection",
                "/help - Show this help message"
            ])
        
        help_lines.extend([
            "\n🚧 **Coming Soon:**",
            "/list - Show all configured wallets",
            "/check - Check wallet balances", 
            "/add - Add a new wallet",
            "/remove - Remove a wallet",
            "\n*More commands will be added in the next phases.*"
        ])
        
        help_text = "\n".join(help_lines)
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
        user_name = update.effective_user.first_name or "User"
        self.logger.info(f"Help command processed for user {user_name}")