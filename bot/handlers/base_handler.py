"""Base handler class for all command handlers."""

import logging
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.config import Config

logger = logging.getLogger(__name__)

class BaseHandler(ABC):
    """Base class for all command handlers."""
    
    def __init__(self):
        self.config = Config
        self.logger = logger
    
    def is_authorized(self, user_id: str) -> bool:
        """Check if user is authorized to use the bot."""
        authorized_users = self.config.get_authorized_users()
        return user_id in authorized_users
    
    async def check_authorization(self, update: Update) -> bool:
        """Check authorization and send error message if unauthorized."""
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.first_name or "User"
        
        # TEMPORARY DEBUG - Add this line
        self.logger.info(f"🔍 AUTH DEBUG: user_id={user_id}, effective_user={update.effective_user.first_name}, chat_id={update.message.chat_id}")

        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ You are not authorized to use this bot.")
            self.logger.warning(f"Unauthorized access attempt from user {user_name} (ID: {user_id})")
            return False
        
        return True
    
    @property
    @abstractmethod
    def command_name(self) -> str:
        """Return the command name (without /)."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the command description for help."""
        pass
    
    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the command."""
        pass