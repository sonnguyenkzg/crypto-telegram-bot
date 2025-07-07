"""Check balance command handler."""

import re
from decimal import Decimal
from typing import Dict, List
from telegram import Update
from telegram.ext import ContextTypes

from .base_handler import BaseHandler
from bot.services.wallet_service import WalletService
from bot.services.balance_service import BalanceService
from bot.utils.quote_parser import extract_quoted_strings, has_unquoted_text

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
        Supports all double quote types: "text", "text"
        
        Args:
            text: Command arguments from Telegram
            
        Returns:
            List[str]: List of parsed inputs (wallet names or addresses)
        """
        if not text or not text.strip():
            return []
        
        # Check for unquoted text (should be rejected)
        if has_unquoted_text(text):
            return ["__UNQUOTED_ERROR__"]
        
        # Extract quoted strings using universal parser
        quoted_inputs = extract_quoted_strings(text)
        
        return quoted_inputs
    
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
    
    def extract_wallet_group(self, wallet_name: str) -> str:
        """
        Extract group code from wallet name (e.g., 'KZP 96G1' -> 'KZP').
        
        Args:
            wallet_name: Full wallet name
            
        Returns:
            str: Group code
        """
        # Split wallet name and get first part as group
        parts = wallet_name.split()
        if len(parts) >= 1:
            return parts[0]  # First part (e.g., "KZP")
        
        # Fallback: use first 3 characters
        return wallet_name[:3].upper()
    
    def format_table_response(self, balances: Dict, successful_checks: int, total_balance: Decimal, time_str: str) -> str:
        """
        Format balance results as a simple table: Group | Wallet Name | Amount.
        
        Args:
            balances: Dictionary of wallet names to balance values
            successful_checks: Number of successful balance fetches
            total_balance: Sum of all balances
            time_str: Formatted time string
            
        Returns:
            str: Formatted table message
        """
        # Count total wallets (including failed ones)
        total_wallets = len(balances)
        
        # Build table header with bold column headers
        table = "```\n"
        table += "Group  │ Wallet Name      │ Amount (USDT)\n"
        table += "───────┼──────────────────┼─────────────\n"
        
        # Sort wallets by group then by name
        wallet_list = []
        for wallet_name, balance in balances.items():
            if balance is not None:
                group_code = self.extract_wallet_group(wallet_name)
                wallet_list.append((group_code, wallet_name, balance))
        
        # Sort by group, then by wallet name
        wallet_list.sort(key=lambda x: (x[0], x[1]))
        
        # Add rows for each wallet
        grand_total = Decimal('0')
        
        for group_code, wallet_name, balance in wallet_list:
            # Truncate wallet name if too long
            display_name = wallet_name[:16] if len(wallet_name) > 16 else wallet_name
            
            table += f"{group_code:6s} │ {display_name:16s} │ {balance:10,.2f}\n"
            grand_total += balance
        
        # Add total row
        table += "───────┼──────────────────┼─────────────\n"
        table += f"{'TOTAL':6s} │ {'':<16s} │ {grand_total:10,.2f}\n"
        table += "```"
        
        # Build complete message
        message = f"🤖 *Wallet Balance Check*\n\n"
        message += f"⏰ *Time:* {time_str} GMT+{self.balance_service.GMT_OFFSET}\n\n"
        message += f"📊 *Total wallets checked*: {total_wallets}\n\n"
        message += f"*Wallet Balances:*\n\n"
        message += table
        
        return message
    
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
        
        # Get current time for display
        time_str = self.balance_service.get_current_gmt_time()
        
        # Format response as table
        message = self.format_table_response(balances, successful_checks, total_balance, time_str)
        
        # Add not found note if any
        if not_found:
            unique_not_found = list(dict.fromkeys(not_found))
            message += f"\n\n❌ **Not found:** {', '.join(unique_not_found)}"
        
        # Update the checking message with results
        await checking_message.edit_text(message, parse_mode='Markdown')
        
        self.logger.info(f"Check command completed for user {user_name}, {successful_checks}/{len(wallets_to_check)} wallets successful")