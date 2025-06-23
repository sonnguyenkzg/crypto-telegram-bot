"""
Daily report service for generating and sending scheduled balance reports.
Handles report generation and formatting for Telegram.
"""

import logging
from decimal import Decimal
from typing import Dict, Optional

from .wallet_service import WalletService
from .balance_service import BalanceService

logger = logging.getLogger(__name__)

class DailyReportService:
    """Service for generating daily balance reports."""
    
    def __init__(self):
        self.wallet_service = WalletService()
        self.balance_service = BalanceService()
    
    async def generate_daily_report(self) -> Optional[str]:
        """
        Generate daily balance report using the same logic as /check command.
        
        Returns:
            Optional[str]: Formatted report message or None if no wallets configured
        """
        try:
            # Load all wallets
            wallet_data = self.wallet_service.load_wallets()
            if not wallet_data:
                logger.warning("No wallets configured for daily report")
                return None
            
            # Get all wallet addresses for checking
            wallets_to_check = {name: info['address'] for name, info in wallet_data.items()}
            
            logger.info(f"Generating daily report for {len(wallets_to_check)} wallets")
            
            # Fetch balances for all wallets
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
                logger.error("Failed to fetch any wallet balances for daily report")
                return "❌ Daily Report Failed\n\nUnable to fetch any wallet balances. Please check network connection."
            
            # Build report message (same format as /check but with daily report title)
            time_str = self.balance_service.get_current_gmt_time()
            title = "💰 *Daily Balance Report*\n"
            time_line = f"⏰ *Time:* {time_str} GMT+{self.balance_service.GMT_OFFSET}"
            
            wallet_list = "\n".join(results)
            footer = f"\n\n📊 *Total:* {total_balance:,.2f} USDT"
            
            if successful_checks < len(wallets_to_check):
                footer += f"\n⚠️ *Note:* {len(wallets_to_check) - successful_checks} wallet(s) failed to fetch"
            
            message = f"{title}\n{time_line}\n\n{wallet_list}{footer}"
            
            logger.info(f"Daily report generated successfully: {successful_checks}/{len(wallets_to_check)} wallets, Total: {total_balance:,.2f} USDT")
            return message
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return f"❌ Daily Report Error\n\nFailed to generate report: {str(e)}"
    
    def format_for_telegram(self, message: str) -> str:
        """
        Format message for Telegram (already in correct format).
        This method exists for consistency with Slack version and future formatting needs.
        
        Args:
            message: The report message
            
        Returns:
            str: Formatted message for Telegram
        """
        # Message is already in correct Telegram format
        # This method can be enhanced later if special formatting is needed
        return message