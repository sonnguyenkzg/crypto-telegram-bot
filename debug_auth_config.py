#!/usr/bin/env python3
"""
Debug script to check what authorized users are being loaded
"""

from bot.utils.config import Config

def debug_authorization():
    """Debug the authorization configuration."""
    print("🔍 Authorization Debug:")
    print("=" * 40)
    
    print(f"Raw AUTHORIZED_USER: '{Config.AUTHORIZED_USER}'")
    print(f"Type: {type(Config.AUTHORIZED_USER)}")
    print(f"Environment: {Config.ENVIRONMENT}")
    
    # Test the split manually
    raw_users = Config.AUTHORIZED_USER
    if raw_users:
        print(f"Contains comma: {',' in raw_users}")
        split_test = raw_users.split(',')
        print(f"Split result: {split_test}")
        stripped_test = [uid.strip() for uid in split_test if uid.strip()]
        print(f"After strip: {stripped_test}")
    
    authorized_users = Config.get_authorized_users()
    print(f"Final parsed authorized users: {authorized_users}")
    print(f"Number of authorized users: {len(authorized_users)}")
    
    your_id = "5005604119"
    print(f"\nYour ID ({your_id}) in list: {your_id in authorized_users}")
    
    # Check each individual ID
    print(f"\nChecking each ID individually:")
    for i, user_id in enumerate(authorized_users):
        print(f"  Index {i}: '{user_id}' (length: {len(user_id)})")
        print(f"    Equals your ID: {user_id == your_id}")
    
    print("\nExpected user IDs:")
    expected = ["5005604119", "1355953362", "7611340376", "7405008177"]
    for user_id in expected:
        status = "✅" if user_id in authorized_users else "❌"
        print(f"  {status} {user_id}")

if __name__ == "__main__":
    debug_authorization()