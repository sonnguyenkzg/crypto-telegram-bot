#!/usr/bin/env python3
"""
Helper script to get team member user IDs
Run this after team members send messages in the group
"""

import asyncio
from telegram import Bot
from bot.utils.config import Config

async def get_team_user_ids():
    """Get user IDs of team members from recent messages."""
    try:
        bot = Bot(Config.TELEGRAM_BOT_TOKEN)
        print("👥 Fetching team member user IDs...")
        
        # Get recent updates
        updates = await bot.get_updates()
        
        if not updates:
            print("❌ No recent updates found")
            print("💡 Ask team members to send a message in the group and run this script again")
            return
        
        # Collect unique users
        users = {}
        
        for update in updates[-20:]:  # Check last 20 updates
            if update.message and update.message.from_user:
                user = update.message.from_user
                users[user.id] = {
                    'name': f"{user.first_name} {user.last_name or ''}".strip(),
                    'username': user.username,
                    'id': user.id
                }
        
        print(f"\n👥 Found {len(users)} unique users:")
        print("=" * 60)
        
        user_ids = []
        for user_id, user_info in users.items():
            username_display = f"@{user_info['username']}" if user_info['username'] else "No username"
            print(f"👤 {user_info['name']}")
            print(f"   User ID: {user_id}")
            print(f"   Username: {username_display}")
            user_ids.append(str(user_id))
            print("-" * 30)
        
        print(f"\n🔧 For your .env file:")
        print(f"AUTHORIZED_USER={','.join(user_ids)}")
        print("\n💡 Copy the user IDs of your team members only!")
        
    except Exception as e:
        print(f"❌ Error getting user IDs: {e}")

if __name__ == "__main__":
    asyncio.run(get_team_user_ids())