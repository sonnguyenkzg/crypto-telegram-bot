#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def test_daily_report():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"Using token: {token}")
    print(f"Using chat_id: {chat_id}")
    
    bot = Bot(token=token)
    
    test_message = """🧪 **Test Daily Report**

💰 Daily Balance Report
⏰ Time: 2025-06-20 13:00 GMT+7

- Test Wallet 1: 0.00 USDT
- Test Wallet 2: 1,234.56 USDT

📊 Total: 1,234.56 USDT"""
    
    try:
        await bot.send_message(chat_id=chat_id, text=test_message, parse_mode='Markdown')
        print("✅ Test daily report sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send test report: {e}")

if __name__ == "__main__":
    asyncio.run(test_daily_report())