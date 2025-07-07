#!/usr/bin/env python3
"""
Daily Balance Report Scheduler for Telegram Bot
Sends automated daily reports at 12:00 AM GMT+7 (midnight)

PRODUCTION VERSION: Fixed threading and clean formatting with table layout
"""

import asyncio
import logging
import schedule
import time
import threading
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict

from telegram import Bot
from telegram.error import TelegramError

from bot.utils.config import Config
from bot.services.daily_report_service import DailyReportService

# Setup logging
logger = Config.setup_logging()

class DailyReportScheduler:
    """Scheduler for daily balance reports."""
    
    def __init__(self):
        self.config = Config
        self.bot = None
        self.report_service = DailyReportService()
        
    async def initialize_bot(self):
        """Initialize Telegram bot."""
        try:
            self.bot = Bot(token=self.config.TELEGRAM_BOT_TOKEN)
            # Test bot connection
            bot_info = await self.bot.get_me()
            logger.info(f"Bot initialized successfully: {bot_info.first_name} (@{bot_info.username})")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
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
    
    def format_daily_report_table(self, wallet_balances: Dict, total_balance: Decimal, time_str: str) -> str:
        """
        Format daily report as a table: Group | Wallet Name | Amount.
        
        Args:
            wallet_balances: Dictionary of wallet names to balance values
            total_balance: Sum of all balances
            time_str: Formatted time string
            
        Returns:
            str: Formatted table message for daily report
        """
        # Count total wallets
        total_wallets = len(wallet_balances)
        
        # Build table header
        table = "```\n"
        table += "Group  │ Wallet Name      │ Amount\n"
        table += "───────┼──────────────────┼─────────────\n"
        
        # Sort wallets by group then by name
        wallet_list = []
        for wallet_name, balance in wallet_balances.items():
            group_code = self.extract_wallet_group(wallet_name)
            wallet_list.append((group_code, wallet_name, balance))
        
        # Sort by group, then by wallet name
        wallet_list.sort(key=lambda x: (x[0], x[1]))
        
        # Add rows for each wallet
        for group_code, wallet_name, balance in wallet_list:
            # Truncate wallet name if too long
            display_name = wallet_name[:16] if len(wallet_name) > 16 else wallet_name
            
            table += f"{group_code:6s} │ {display_name:16s} │ {balance:10,.2f}\n"
        
        # Add total row
        table += "───────┼──────────────────┼─────────────\n"
        table += f"{'TOTAL':6s} │ {'':<16s} │ {total_balance:10,.2f}\n"
        table += "```"
        
        # Build complete daily report message
        message = f"💰 *Daily Balance Report*\n\n"
        message += f"🕛 *Time:* {time_str}\n\n"
        message += f"📊 *Total wallets checked:* {total_wallets}\n\n"
        message += f"*Wallet Balances:*\n\n"
        message += table
        
        return message
    
    async def send_daily_report(self):
        """Generate and send daily balance report."""
        try:
            logger.info("🚀 STARTING SCHEDULED DAILY REPORT")
            logger.info(f"🕐 Report time: {datetime.now()}")
            
            # Create fresh bot instance for this thread
            fresh_bot = Bot(token=self.config.TELEGRAM_BOT_TOKEN)
            
            # Generate the raw report using existing service
            from bot.services.wallet_service import WalletService
            from bot.services.balance_service import BalanceService
            
            wallet_service = WalletService()
            balance_service = BalanceService()
            
            # Load wallets and fetch balances
            wallet_data = wallet_service.load_wallets()
            if not wallet_data:
                logger.warning("No wallets configured for daily report")
                return
            
            # Prepare wallets for balance checking
            wallets_to_check = {name: info['address'] for name, info in wallet_data.items()}
            
            # Fetch all balances
            balances = balance_service.fetch_multiple_balances(wallets_to_check)
            
            # Calculate total and filter successful balances
            total_balance = Decimal('0')
            wallet_balances = {}
            
            for wallet_name, balance in balances.items():
                if balance is not None:
                    wallet_balances[wallet_name] = balance
                    total_balance += balance
            
            if not wallet_balances:
                logger.warning("No successful balance fetches for daily report")
                return
            
            # Get current GMT+7 time for display
            gmt7_time = datetime.now(timezone(timedelta(hours=7)))
            time_str = gmt7_time.strftime('%Y-%m-%d %H:%M GMT+7')
            
            # Format as table
            report_message = self.format_daily_report_table(wallet_balances, total_balance, time_str)
            
            # Send report to specific topic
            if self.config.TELEGRAM_CHAT_ID:
                topic_id = getattr(self.config, 'DAILY_REPORTS_TOPIC_ID', None)
                
                send_params = {
                    'chat_id': self.config.TELEGRAM_CHAT_ID,
                    'text': report_message,
                    'parse_mode': 'Markdown'
                }
                
                # Add topic ID if configured
                if topic_id:
                    send_params['message_thread_id'] = int(topic_id)
                
                await fresh_bot.send_message(**send_params)
                logger.info(f"✅ Daily report sent successfully to chat {self.config.TELEGRAM_CHAT_ID}")
            else:
                logger.error("❌ TELEGRAM_CHAT_ID not configured")
                
        except TelegramError as e:
            logger.error(f"❌ Telegram error sending daily report: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error in daily report: {e}")
    
    def run_scheduled_report(self):
        """Wrapper to run async report in separate thread."""
        def thread_target():
            try:
                logger.info("📞 SCHEDULED REPORT TRIGGERED!")
                
                # Create completely new event loop in this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    loop.run_until_complete(self.send_daily_report())
                    logger.info("✅ Scheduled report completed")
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"❌ Error in scheduled report thread: {e}")
        
        # Run in separate thread to avoid event loop conflicts
        thread = threading.Thread(target=thread_target)
        thread.start()
        thread.join()  # Wait for completion

def main():
    """Main function to run the daily report scheduler."""
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Create scheduler instance
        scheduler = DailyReportScheduler()
        
        # Initialize bot
        async def init_bot():
            return await scheduler.initialize_bot()
        
        if not asyncio.run(init_bot()):
            logger.error("Failed to initialize bot, exiting")
            return
        
        # Schedule daily report at 17:00 UTC (midnight GMT+7)
        schedule.every().day.at("17:00").do(scheduler.run_scheduled_report)
        
        # Get current time info
        utc_now = datetime.now(timezone.utc)
        gmt7_now = datetime.now(timezone(timedelta(hours=7)))
        
        logger.info("=== Daily Report Scheduler Started ===")
        logger.info(f"Environment: {Config.ENVIRONMENT}")
        logger.info(f"Bot Token: ...{Config.TELEGRAM_BOT_TOKEN[-10:] if Config.TELEGRAM_BOT_TOKEN else 'Not set'}")
        logger.info(f"Chat ID: {Config.TELEGRAM_CHAT_ID}")
        logger.info(f"Current UTC time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Current GMT+7 time: {gmt7_now.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("📅 Scheduled: Daily reports at 17:00 UTC (00:00 GMT+7)")
        
        # Show next scheduled run
        jobs = schedule.get_jobs()
        if jobs:
            next_run = jobs[0].next_run
            next_run_gmt7 = next_run.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=7)))
            logger.info(f"⏰ Next report: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            logger.info(f"   (Which is: {next_run_gmt7.strftime('%Y-%m-%d %H:%M:%S')} GMT+7)")
        
        logger.info("Press Ctrl+C to stop")
        logger.info("=====================================")
        
        # Run scheduler
        loop_count = 0
        while True:
            loop_count += 1
            
            # Log every 60 loops (60 minutes) to show it's alive
            if loop_count % 60 == 0:
                current_time = datetime.now()
                logger.info(f"🔄 Scheduler alive - Loop #{loop_count}, Time: {current_time}")
                
                # Show next scheduled time
                jobs = schedule.get_jobs()
                if jobs:
                    next_run = jobs[0].next_run
                    logger.info(f"⏰ Next scheduled run: {next_run}")
            
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("Daily report scheduler stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in daily report scheduler: {e}")
        raise

def test_report():
    """Test function to send a report immediately (for testing)."""
    async def run_test():
        scheduler = DailyReportScheduler()
        if await scheduler.initialize_bot():
            logger.info("Sending test report...")
            await scheduler.send_daily_report()
        else:
            logger.error("Failed to initialize bot for test")
    
    asyncio.run(run_test())

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode: send report immediately
        test_report()
    else:
        # Normal mode: run scheduler
        main()