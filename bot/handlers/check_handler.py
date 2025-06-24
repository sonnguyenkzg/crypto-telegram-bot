"""Check balance command handler."""

import re
from decimal import Decimal
from typing import Dict, List
from telegram import Update
from telegram.ext import ContextTypes

from .base_handler import BaseHandler
from bot.services.wallet_service import WalletService
from bot.services.balance_service import BalanceService

class CheckHandler(BaseHandler):
    """Handler for the /check command."""
    
    def __init__(self):
        super().__init__()
        self.wallet_service = WalletService()
        self.balance_service = BalanceService()
    
    @property
    def command_name(self) -> str:
        return "check"
    
    @property
    def description(self) -> str:
        return "Check wallet balances (all wallets or specific ones)"
    
    def parse_check_arguments(self, text: str) -> List[str]:
        """
        Parse quoted arguments from check command text.
        Now with STRICT quote validation - rejects unquoted text.
        
        Args:
            text: Command arguments from Telegram
            
        Returns:
            List[str]: List of parsed inputs (wallet names or addresses)
        """
        if not text or not text.strip():
            return []
        
        # Clean the text first - remove markdown formatting (same as Slack)
        cleaned_text = text.strip()
        
        # Remove common markdown patterns that might interfere
        cleaned_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_text)  # Remove **bold**
        cleaned_text = re.sub(r'\*([^*]+)\*', r'\1', cleaned_text)      # Remove *italic*
        cleaned_text = re.sub(r'`([^`]+)`', r'\1', cleaned_text)        # Remove `code`
        
        # Find quoted strings - use only one pattern to avoid duplicates
        quoted_inputs = re.findall(r'"([^"]*)"', cleaned_text)
        
        # NEW: Check if user provided unquoted text (should be rejected)
        has_text_without_quotes = cleaned_text.strip() and not quoted_inputs
        
        if has_text_without_quotes:
            # Return special marker to indicate unquoted text error
            return ["__UNQUOTED_ERROR__"]
        
        # Filter out empty inputs and remove duplicates
        valid_inputs = []
        for inp in quoted_inputs:
            cleaned_inp = inp.strip()
            if cleaned_inp and cleaned_inp not in valid_inputs:
                valid_inputs.append(cleaned_inp)
        
        return valid_inputs
    
    def resolve_wallets_to_check(self, inputs: List[str], wallet_data: Dict) -> tuple:
        """
        Resolve input arguments to {display_name: address} mapping.
        
        Args:
            inputs: List of wallet names or addresses from user
            wallet_data: All available wallet data
            
        Returns:
            tuple: (wallets_to_check, not_found_list)
        """
        wallets_to_check = {}
        not_found = []
        
        for input_str in inputs:
            input_str = input_str.strip()
            if not input_str:
                continue
                
            # Check if input is a TRC20 address
            if self.balance_service.validate_trc20_address(input_str):
                # It's an address - find the wallet name or use address as display (case-insensitive)
                found_wallet = False
                for wallet_name, wallet_info in wallet_data.items():
                    if wallet_info['address'].lower() == input_str.lower():
                        wallets_to_check[wallet_name] = wallet_info['address']  # Use original case from JSON
                        found_wallet = True
                        break
                
                if not found_wallet:
                    # Address not in our monitored list - still check it (use original case)
                    display_name = f"External: {input_str[:10]}...{input_str[-6:]}"
                    wallets_to_check[display_name] = input_str
            
            else:
                # It's a wallet name - find the address (case-insensitive matching)
                found_wallet = False
                for wallet_name, wallet_info in wallet_data.items():
                    if wallet_name.lower() == input_str.lower():
                        wallets_to_check[wallet_name] = wallet_info['address']
                        found_wallet = True
                        break
                
                if not found_wallet:
                    not_found.append(input_str)
        
        return wallets_to_check, not_found
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /check command."""
        user_name = update.effective_user.first_name or "User"
        user_id = str(update.effective_user.id)
        
        self.logger.info(f"Check command received from user {user_name} (ID: {user_id})")
        
        # Check authorization
        if not await self.check_authorization(update):
            return
        
        # Load all wallets
        wallet_data = self.wallet_service.load_wallets()
        if not wallet_data:
            await update.message.reply_text("❌ No wallets configured\n\nUse `/add` to add your first wallet.", parse_mode='Markdown')
            return
        
        # Get command text (everything after /check)
        command_text = ""
        if context.args:
            command_text = " ".join(context.args)
        
        # Parse inputs from text (if any)
        inputs = self.parse_check_arguments(command_text)
        not_found = []  # Initialize empty list for all cases
        
        # Check for unquoted text error
        if inputs == ["__UNQUOTED_ERROR__"]:
            available_names = ', '.join(list(wallet_data.keys())[:5])
            if len(wallet_data) > 5:
                available_names += "..."
                
            usage_message = f"""❌ No valid wallet names or addresses found in: `{command_text}`

*Note:* All wallet names and addresses must be in quotes!

*Usage:*
• `/check` - Check all wallets
• `/check "wallet_name"` - Check by wallet name  
• `/check "TRC20_address"` - Check by address
• `/check "wallet1" "wallet2"` - Multiple wallets

*Available wallet names:*
{available_names}

*Examples:*
• `/check "KZP 96G1"`
• `/check "TNZJ5wTSMK4oR79CYzy8BGK6LWNmQxcuM8"`"""
            
            await update.message.reply_text(usage_message, parse_mode='Markdown')
            return
        
        if not inputs:
            # Check all wallets
            wallets_to_check = {name: info['address'] for name, info in wallet_data.items()}
        else:
            # Resolve inputs to wallets
            wallets_to_check, not_found = self.resolve_wallets_to_check(inputs, wallet_data)
            
            # If no valid wallets found but we had inputs, show error
            if not wallets_to_check and not_found:
                available_names = ', '.join(list(wallet_data.keys())[:5])
                if len(wallet_data) > 5:
                    available_names += "..."
                
                error_message = f"""❌ Wallet name(s) not found: {', '.join(not_found)}

*Available wallet names:*
{available_names}

Use `/list` to see all wallets or provide TRC20 addresses directly."""
                
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
        
        # Show "checking..." message for user feedback
        checking_message = await update.message.reply_text("🔄 Checking balances...")
        
        # Fetch balances
        balances = self.balance_service.fetch_multiple_balances(wallets_to_check)
        
        # Process results
        results = []
        total_balance = Decimal('0')
        successful_checks = 0
        
        for display_name, balance in balances.items():
            if balance is not None:
                results.append(f"• *{display_name}*: {balance:,.2f} USDT")
                total_balance += balance
                successful_checks += 1
            else:
                results.append(f"• *{display_name}*: ❌ Unable to fetch balance")
        
        # Handle no successful checks
        if successful_checks == 0:
            error_msg = "❌ Unable to fetch any wallet balances. Please check your network connection."
            if not_found:
                # Remove duplicates and join
                unique_not_found = list(dict.fromkeys(not_found))
                error_msg += f"\n\n❌ *Not found:* {', '.join(unique_not_found)}"
            await checking_message.edit_text(error_msg, parse_mode='Markdown')
            return
        
        # Build response message (same format as Slack with title)
        time_str = self.balance_service.get_current_gmt_time()
        title = "🤖 *Wallet Balance Check*\n"
        
        if len(wallets_to_check) == 1:
            # Single wallet response
            time_line = f"⏰ *Time:* {time_str} GMT+{self.balance_service.GMT_OFFSET}"
            wallet_list = "\n".join(results)
            message = f"{title}\n{time_line}\n\n{wallet_list}"
            
            # Add not found note for single wallet if needed
            if not_found:
                # Remove duplicates and join
                unique_not_found = list(dict.fromkeys(not_found))
                message += f"\n\n⚠️ *Not found:* {', '.join(unique_not_found)}"
        else:
            # Multiple wallets response
            time_line = f"⏰ *Time:* {time_str} GMT+{self.balance_service.GMT_OFFSET}"
            footer = f"\n\n📊 *Total:* {total_balance:,.2f} USDT"
            
            if successful_checks < len(wallets_to_check):
                footer += f"\n⚠️ *Note:* {len(wallets_to_check) - successful_checks} wallet(s) failed to fetch"
            
            # Add not found wallets note
            if not_found:
                # Remove duplicates and join
                unique_not_found = list(dict.fromkeys(not_found))
                footer += f"\n❌ *Not found:* {', '.join(unique_not_found)}"
            
            wallet_list = "\n".join(results)
            message = f"{title}\n{time_line}\n\n{wallet_list}{footer}"
        
        # Update the checking message with results
        await checking_message.edit_text(message, parse_mode='Markdown')
        
        self.logger.info(f"Check command completed for user {user_name}, {successful_checks}/{len(wallets_to_check)} wallets successful")