#!/usr/bin/env python3
"""
Daily Balance Report Scheduler for Telegram Bot
Sends automated daily reports at 12:00 AM GMT+7 (midnight)

PRODUCTION VERSION: Fixed threading and clean formatting
"""

import asyncio
import logging
import schedule
import time
import threading
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
            logger.info("🚀 STARTING SCHEDULED DAILY REPORT")
            logger.info(f"🕐 Report time: {datetime.now()}")
            
            # Create fresh bot instance for this thread
            fresh_bot = Bot(token=self.config.TELEGRAM_BOT_TOKEN)
            
            # Generate report
            report_message = await self.report_service.generate_daily_report()
            
            if not report_message:
                logger.warning("No report generated (no wallets configured)")
                return
            
            # Add timestamp to report (clean format)
            gmt7_time = datetime.now(timezone(timedelta(hours=7)))
            report_with_timestamp = f"🕛 **Time: {gmt7_time.strftime('%Y-%m-%d %H:%M')} GMT+7**\n\n{report_message}"
            
            # Send to Telegram with fresh bot instance
            if self.config.TELEGRAM_CHAT_ID:
                await fresh_bot.send_message(
                    chat_id=self.config.TELEGRAM_CHAT_ID,
                    text=report_with_timestamp,
                    parse_mode='Markdown'
                )
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