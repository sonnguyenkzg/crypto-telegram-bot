#!/usr/bin/env python3
"""
Daily Balance Report Scheduler for Telegram Bot
Sends automated daily reports at 12:00 AM GMT+7 (midnight)

Same functionality as the Slack version but for Telegram.
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timezone, timedelta

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
    
    async def send_daily_report(self):
        """Generate and send daily balance report."""
        try:
            logger.info("Starting daily report generation...")
            
            # Generate report
            report_message = await self.report_service.generate_daily_report()
            
            if not report_message:
                logger.warning("No report generated (no wallets configured)")
                return
            
            # Send to Telegram
            if self.config.TELEGRAM_CHAT_ID:
                await self.bot.send_message(
                    chat_id=self.config.TELEGRAM_CHAT_ID,
                    text=report_message,
                    parse_mode='Markdown'
                )
                logger.info(f"Daily report sent successfully to chat {self.config.TELEGRAM_CHAT_ID}")
            else:
                logger.error("TELEGRAM_CHAT_ID not configured")
                
        except TelegramError as e:
            logger.error(f"Telegram error sending daily report: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in daily report: {e}")
    
    def run_scheduled_report(self):
        """Wrapper to run async report in sync context."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async report
            loop.run_until_complete(self.send_daily_report())
            loop.close()
            
        except Exception as e:
            logger.error(f"Error in scheduled report wrapper: {e}")

def main():
    """Main function to run the daily report scheduler."""
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Create scheduler instance
        scheduler = DailyReportScheduler()
        
        # Initialize bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if not loop.run_until_complete(scheduler.initialize_bot()):
            logger.error("Failed to initialize bot, exiting")
            return
        
        loop.close()
        
        # Schedule daily report at midnight GMT+7
        schedule.every().day.at("00:00").do(scheduler.run_scheduled_report)
        
        # Get current time in GMT+7
        gmt7_tz = timezone(timedelta(hours=7))
        current_time = datetime.now(gmt7_tz)
        
        logger.info("=== Daily Report Scheduler Started ===")
        logger.info(f"Environment: {Config.ENVIRONMENT}")
        logger.info(f"Bot Token: ...{Config.TELEGRAM_BOT_TOKEN[-10:] if Config.TELEGRAM_BOT_TOKEN else 'Not set'}")
        logger.info(f"Chat ID: {Config.TELEGRAM_CHAT_ID}")
        logger.info(f"Current time (GMT+7): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("Scheduled: Daily reports at 00:00 GMT+7 (midnight)")
        logger.info("Press Ctrl+C to stop")
        logger.info("=====================================")
        
        # Run scheduler
        while True:
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