"""Add wallet command handler."""

import re
from typing import Tuple, List, Union
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.quote_parser import extract_quoted_strings, has_unquoted_text
from .base_handler import BaseHandler
from bot.services.wallet_service import WalletService

class AddHandler(BaseHandler):
    """Handler for the /add command."""
    
    def __init__(self):
        super().__init__()
        self.wallet_service = WalletService()
    
    @property
    def command_name(self) -> str:
        return "add"
    
    @property
    def description(self) -> str:
        return "Add a new wallet (requires 3 quoted arguments)"
    
    def parse_quoted_arguments(self, text: str) -> Tuple[bool, Union[List[str], str]]:
        """
        Parse text with quoted arguments.
        Expects exactly 3 quoted strings: "company" "wallet" "address"
        
        Args:
            text: Command text from Telegram
            
        Returns:
            Tuple[bool, Union[List[str], str]]: (success, [company, wallet, address] or error_message)
        """
        if not text or not text.strip():
            return False, "❌ Missing arguments"
        
        # Extract quoted strings using universal parser
        matches = extract_quoted_strings(text)
        
        if len(matches) != 3:
            return False, f"❌ Expected 3 quoted arguments, found {len(matches)}"
        
        company, wallet, address = matches
        
        # Validate none are empty
        if not company.strip():
            return False, "❌ Company cannot be empty"
        if not wallet.strip():
            return False, "❌ Wallet name cannot be empty"  
        if not address.strip():
            return False, "❌ Address cannot be empty"
        
        return True, [company.strip(), wallet.strip(), address.strip()]
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /add command."""
        user_name = update.effective_user.first_name or "User"
        user_id = str(update.effective_user.id)
        
        self.logger.info(f"Add command received from user {user_name} (ID: {user_id})")
        
        # Check authorization
        if not await self.check_authorization(update):
            return
        
        # Get command text (everything after /add)
        command_text = ""
        if context.args:
            # Join all arguments back together to preserve quotes
            command_text = " ".join(context.args)
        
        # If no arguments or command_text is empty, show usage
        if not command_text.strip():
            error_message = """❌ Missing arguments

*Usage:* `/add "company" "wallet_name" "address"`
*Example:* `/add "KZP" "KZP WDB2" "TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS"`"""
            
            await update.message.reply_text(error_message, parse_mode='Markdown')
            return
        
        # Parse arguments using strict quoted parsing
        success, result = self.parse_quoted_arguments(command_text)
        
        if not success:
            error_msg = result
            usage_message = f"""{error_msg}

*Usage:* `/add "company" "wallet_name" "address"`
*Example:* `/add "KZP" "KZP WDB2" "TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS"`"""
            
            await update.message.reply_text(usage_message, parse_mode='Markdown')
            self.logger.warning(f"Add command failed for user {user_name}: {error_msg}")
            return
        
        company, wallet, address = result
        
        # Attempt to add wallet using wallet service
        success, message = self.wallet_service.add_wallet(company, wallet, address)
        
        if success:
            # Format success message exactly like Slack
            success_message = f"""✅ *Wallet Added Successfully*

📋 *Details:*
• Company: {company}
• Wallet: {wallet}
• Address: {address}

Use `/check` to see current balance."""
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            self.logger.info(f"Wallet '{wallet}' added successfully by user {user_name}")
        else:
            # Send error message from wallet service
            await update.message.reply_text(message, parse_mode='Markdown')
            self.logger.warning(f"Add wallet failed for user {user_name}: {message}")