#!/usr/bin/env python3
"""
Helper script to get Telegram group chat ID
Run this after adding the bot to your group and sending a test message
"""

import asyncio
from telegram import Bot
from bot.utils.config import Config

async def get_group_chat_id():
    """Get recent chat IDs to find your group."""
    try:
        bot = Bot(Config.TELEGRAM_BOT_TOKEN)
        print("🔍 Fetching recent chat updates...")
        
        # Get recent updates
        updates = await bot.get_updates()
        
        if not updates:
            print("❌ No recent updates found")
            print("💡 Send a message in your group (like /start) and run this script again")
            return
        
        print(f"\n📋 Found {len(updates)} recent updates:")
        print("=" * 50)
        
        for update in updates[-10:]:  # Show last 10 updates
            if update.message and update.message.chat:
                chat = update.message.chat
                user = update.message.from_user
                
                chat_type_icon = {
                    'private': '👤',
                    'group': '👥', 
                    'supergroup': '👥',
                    'channel': '📢'
                }.get(chat.type, '❓')
                
                print(f"{chat_type_icon} Chat Type: {chat.type}")
                print(f"💬 Chat ID: {chat.id}")
                print(f"📝 Title: {chat.title or chat.first_name or 'No title'}")
                print(f"👤 From: {user.first_name if user else 'Unknown'}")
                print(f"💭 Message: {update.message.text[:50]}...")
                print("-" * 30)
        
        print("\n🎯 For your team group:")
        print("1. Look for chat.type = 'group' or 'supergroup'")
        print("2. Find your group by title name")
        print("3. Copy the Chat ID (starts with negative number like -1001234567890)")
        print("4. Update TELEGRAM_CHAT_ID in your .env file")
        
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")

if __name__ == "__main__":
    asyncio.run(get_group_chat_id())