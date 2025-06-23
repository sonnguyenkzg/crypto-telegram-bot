#!/usr/bin/env python3
"""
Disable bot command auto-complete by clearing command list
Run this once to remove the auto-suggest feature
"""

import asyncio
from telegram import Bot
from bot.utils.config import Config

async def disable_autocomplete():
    """Remove bot commands to disable auto-complete."""
    try:
        bot = Bot(Config.TELEGRAM_BOT_TOKEN)
        
        # Clear all bot commands (removes auto-complete)
        await bot.delete_my_commands()
        
        print("✅ Bot command auto-complete disabled")
        print("💡 Users won't see command suggestions when typing /")
        
    except Exception as e:
        print(f"❌ Error disabling auto-complete: {e}")

if __name__ == "__main__":
    asyncio.run(disable_autocomplete())