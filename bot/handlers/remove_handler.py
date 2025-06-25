"""Remove wallet command handler."""

import re
from typing import Tuple, Union
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.quote_parser import extract_quoted_strings, has_unquoted_text
from .base_handler import BaseHandler
from bot.services.wallet_service import WalletService

class RemoveHandler(BaseHandler):
    """Handler for the /remove command."""
    
    def __init__(self):
        super().__init__()
        self.wallet_service = WalletService()
    
    @property
    def command_name(self) -> str:
        return "remove"
    
    @property
    def description(self) -> str:
        return "Remove a wallet (requires 1 quoted wallet name)"
    
    def parse_single_quoted_argument(self, text: str) -> Tuple[bool, Union[str, str]]:
        """
        Parse text with single quoted argument.
        Expects exactly 1 quoted string: "wallet_name"
        
        Args:
            text: Command text from Telegram
            
        Returns:
            Tuple[bool, Union[str, str]]: (success, wallet_name or error_message)
        """
        if not text or not text.strip():
            return False, "❌ Missing wallet name"
        
        # Extract quoted strings using universal parser
        matches = extract_quoted_strings(text)
        
        if len(matches) != 1:
            return False, f"❌ Expected 1 quoted argument, found {len(matches)}"
        
        wallet_name = matches[0].strip()
        
        # Validate wallet name is not empty
        if not wallet_name:
            return False, "❌ Wallet name cannot be empty"
        
        return True, wallet_name
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /remove command."""
        user_name = update.effective_user.first_name or "User"
        user_id = str(update.effective_user.id)
        
        self.logger.info(f"Remove command received from user {user_name} (ID: {user_id})")
        
        # Check authorization
        if not await self.check_authorization(update):
            return
        
        # Get command text (everything after /remove)
        command_text = ""
        if context.args:
            # Join all arguments back together to preserve quotes
            command_text = " ".join(context.args)
        
        # If no arguments, show usage
        if not command_text.strip():
            usage_message = """❌ Missing wallet name

*Usage:* `/remove "wallet_name"`
*Example:* `/remove "KZP TEST1"`

💡 Use `/list` to see available wallets"""
            
            await update.message.reply_text(usage_message, parse_mode='Markdown')
            return
        
        # Parse argument using strict quoted parsing
        success, result = self.parse_single_quoted_argument(command_text)
        
        if not success:
            error_msg = result
            usage_message = f"""{error_msg}

*Usage:* `/remove "wallet_name"`
*Example:* `/remove "KZP TEST1"`

💡 Use `/list` to see available wallets"""
            
            await update.message.reply_text(usage_message, parse_mode='Markdown')
            self.logger.warning(f"Remove command failed for user {user_name}: {error_msg}")
            return
        
        wallet_name = result
        
        # Check if wallet exists before attempting removal (better UX)
        if not self.wallet_service.wallet_exists(wallet_name):
            # Get similar wallet names for helpful suggestion
            all_wallets = self.wallet_service.load_wallets()
            similar_names = [name for name in all_wallets.keys() if wallet_name.lower() in name.lower()]
            
            error_message = f"❌ Wallet *{wallet_name}* not found"
            
            if similar_names:
                error_message += f"\n\n💡 Did you mean: {', '.join(f'`{name}`' for name in similar_names[:3])}"
            
            error_message += "\n\n📋 Use `/list` to see all available wallets"
            
            await update.message.reply_text(error_message, parse_mode='Markdown')
            self.logger.warning(f"Remove failed - wallet '{wallet_name}' not found for user {user_name}")
            return
        
        # Show confirmation with wallet details before removal
        wallet_info = self.wallet_service.get_wallet_by_name(wallet_name)
        confirm_message = f"""⚠️ *Confirm Wallet Removal*

*Wallet:* {wallet_name}
*Company:* {wallet_info.get('company', 'Unknown')}
*Address:* `{wallet_info.get('address', 'Unknown')}`

Are you sure you want to remove this wallet?

Reply with `/remove "{wallet_name}"` again to confirm."""
        
        # For simplicity, proceed with removal directly (skip confirmation step)
        # In production, you might want to implement a confirmation flow
        
        # Attempt to remove wallet using wallet service
        success, message = self.wallet_service.remove_wallet(wallet_name)
        
        if success:
            # Format success message (enhanced from Slack version)
            success_message = f"""✅ *Wallet Removed Successfully*

*Wallet:* {wallet_name}
*Company:* {wallet_info.get('company', 'Unknown')}

The wallet has been removed from monitoring.
Use `/list` to see remaining wallets."""
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            self.logger.info(f"Wallet '{wallet_name}' removed successfully by user {user_name}")
        else:
            # Send error message from wallet service
            await update.message.reply_text(message, parse_mode='Markdown')
            self.logger.error(f"Remove wallet failed for user {user_name}: {message}")