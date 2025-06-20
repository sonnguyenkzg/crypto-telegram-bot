# bot/telegram_config.py
"""
Configuration settings for the Telegram USDT wallet bot.
Environment variables and system settings.
"""
import os
import subprocess

# Force load secure secrets IMMEDIATELY when module is imported
def _load_secure_secrets():
    """Load secrets from secure location if available"""
    secure_config_path = "/opt/usdt-bot-secrets/config"
    
    if os.path.exists(secure_config_path):
        try:
            # Read the secure config file
            result = subprocess.run(
                ["sudo", "cat", secure_config_path], 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=5
            )
            
            # Parse and set environment variables
            for line in result.stdout.strip().split('\n'):
                if line.startswith('export ') and ('TELEGRAM_' in line or 'USDT_' in line):
                    # Remove 'export ' and parse KEY="value"
                    env_line = line[7:]  # Remove 'export '
                    if '=' in env_line:
                        key, value = env_line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"\'')
                        os.environ[key] = value
            
            print("✅ Loaded secrets from secure storage")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not load secure secrets: {e}")
            return False
    
    return False

# Load secure secrets immediately when this module is imported
_load_secure_secrets()

# Fallback to .env only if secure loading failed
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

# --- Telegram Bot Credentials ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Channel/group ID for reports

# --- API Configuration ---
API_TIMEOUT = 10  # seconds for API requests
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # Official USDT TRC20 contract

# --- File Paths ---
WALLETS_FILE = "wallets.json"
CSV_FILE = "wallet_balances.csv"

# --- Timezone ---
GMT_OFFSET = 7  # GMT+7 timezone offset

# --- Access Control ---
if os.getenv('ENVIRONMENT') == 'prod':
    # Production authorized Telegram user IDs
    ALLOWED_TELEGRAM_USERS = [
        5005604119,   # Son Nguyen (@sonnq35)
        # Add more user IDs as needed
    ]
else:
    # Development authorized Telegram user IDs  
    ALLOWED_TELEGRAM_USERS = [
        5005604119,   # Son Nguyen (@sonnq35)
        # Add more user IDs as needed
    ]

# --- Bot Configuration ---
BOT_USERNAME = "usdt_wallet_monitor_bot"  # Your bot's username (without @)
COMMAND_PREFIX = "/"  # Telegram standard command prefix