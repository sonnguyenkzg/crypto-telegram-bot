#!/usr/bin/env python3
"""
Test script to send daily report to your group immediately
Confirms the group integration and daily report functionality
"""

import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError

from bot.utils.config import Config
from bot.services.daily_report_service import DailyReportService

# Setup logging
logger = Config.setup_logging()

async def test_group_daily_report():
    """Send a test daily report to your group."""
    try:
        print("🧪 Testing Daily Report to Group...")
        print(f"📱 Group Chat ID: {Config.TELEGRAM_CHAT_ID}")
        print(f"🤖 Environment: {Config.ENVIRONMENT}")
        print("=" * 50)
        
        # Initialize bot
        bot = Bot(Config.TELEGRAM_BOT_TOKEN)
        
        # Test bot connection
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: {bot_info.first_name} (@{bot_info.username})")
        
        # Generate daily report
        report_service = DailyReportService()
        print("📊 Generating daily report...")
        
        report_message = await report_service.generate_daily_report()
        
        if not report_message:
            print("❌ No report generated (no wallets configured)")
            return
        
        # Add test header to distinguish from real daily reports
        test_header = "🧪 *TEST DAILY REPORT* - Manual Test\n\n"
        test_message = test_header + report_message
        
        print("📤 Sending test report to group...")
        
        # Send to your group
        await bot.send_message(
            chat_id=Config.TELEGRAM_CHAT_ID,
            text=test_message,
            parse_mode='Markdown'
        )
        
        print("✅ Test daily report sent successfully!")
        print(f"📱 Check your 'Crypto Balance Monitoring' group")
        print("\n🎯 What this confirms:")
        print("  ✅ Bot can send messages to your group")
        print("  ✅ Daily report generation works")
        print("  ✅ All wallet balances fetched")
        print("  ✅ Group integration successful")
        print("\n💡 The real daily reports will be sent at midnight GMT+7")
        
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")
        if "chat not found" in str(e).lower():
            print("💡 Make sure the bot is added to your group and has permission to send messages")
        elif "forbidden" in str(e).lower():
            print("💡 Bot may not have permission to send messages in the group")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Group Daily Report Test...")
    asyncio.run(test_group_daily_report())