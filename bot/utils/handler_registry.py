"""Handler registry for managing command handlers."""

import logging
from typing import Dict, List
from telegram.ext import Application, CommandHandler

from bot.handlers.base_handler import BaseHandler

logger = logging.getLogger(__name__)

class HandlerRegistry:
    """Registry for managing and registering command handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, BaseHandler] = {}
    
    def register_handler(self, handler: BaseHandler) -> None:
        """Register a command handler."""
        command_name = handler.command_name
        
        if command_name in self._handlers:
            logger.warning(f"Handler for command '{command_name}' already exists. Overriding.")
        
        self._handlers[command_name] = handler
        logger.info(f"Registered handler for command: /{command_name}")
    
    def get_handler(self, command_name: str) -> BaseHandler:
        """Get a specific handler by command name."""
        return self._handlers.get(command_name)
    
    def get_all_handlers(self) -> List[BaseHandler]:
        """Get all registered handlers."""
        return list(self._handlers.values())
    
    def register_with_application(self, app: Application) -> None:
        """Register all handlers with the Telegram application."""
        for command_name, handler in self._handlers.items():
            # Create the telegram command handler
            telegram_handler = CommandHandler(command_name, handler.handle)
            app.add_handler(telegram_handler)
            logger.info(f"Added Telegram handler for /{command_name}")
        
        logger.info(f"Total handlers registered with application: {len(self._handlers)}")
    
    def list_commands(self) -> List[str]:
        """Get list of all registered command names."""
        return list(self._handlers.keys())
    
    def get_commands_summary(self) -> str:
        """Get a formatted summary of all commands."""
        if not self._handlers:
            return "No commands registered."
        
        summary_lines = []
        for handler in self._handlers.values():
            summary_lines.append(f"/{handler.command_name} - {handler.description}")
        
        return "\n".join(summary_lines)