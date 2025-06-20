#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from wallet_manager import WalletManager

load_dotenv()

async def test_send_daily_report():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # Generate the report
    wallet_manager = WalletManager()
    report = await wallet_manager.generate_daily_report()
    
    # Send it via Telegram
    bot = Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text=report, parse_mode='Markdown')
        print("✅ Daily report sent successfully to Telegram!")
    except Exception as e:
        print(f"❌ Failed to send daily report: {e}")

if __name__ == "__main__":
    asyncio.run(test_send_daily_report())