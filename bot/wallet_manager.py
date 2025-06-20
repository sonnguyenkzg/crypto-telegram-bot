# bot/wallet_manager.py
"""
Core wallet management functions.
Handles loading, saving, adding, and removing wallets from JSON storage.
"""
import json
import re
from typing import Dict, Tuple

from bot.telegram_config import WALLETS_FILE


def load_wallets() -> Dict[str, Dict[str, str]]:
    """
    Load wallet data from JSON file.
    
    Returns:
        Dict: Full wallet data structure with metadata
    """
    try:
        with open(WALLETS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Wallet file {WALLETS_FILE} not found")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing wallet JSON: {e}")
        return {}
    except Exception as e:
        print(f"Error loading wallets: {e}")
        return {}


def save_wallets(wallet_data: Dict[str, Dict[str, str]]) -> bool:
    """
    Save wallet data to JSON file.
    
    Args:
        wallet_data: Full wallet data structure
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving wallets: {e}")
        return False


def validate_trc20_address(address: str) -> bool:
    """
    Validate TRC20 address format.
    
    Args:
        address: TRC20 address to validate
        
    Returns:
        bool: True if valid TRC20 format
    """
    # TRC20 addresses start with 'T' and are exactly 34 characters
    pattern = r'^T[A-Za-z0-9]{33}$'
    return bool(re.match(pattern, address))


def add_wallet(company: str, wallet_name: str, address: str) -> Tuple[bool, str]:
    """
    Add a new wallet to the storage.
    
    Args:
        company: Company code (e.g., "KZP")
        wallet_name: Wallet identifier (e.g., "TH BM 1")
        address: TRC20 wallet address
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Validate inputs
    if not company or not company.strip():
        return False, "❌ Company cannot be empty"
    
    if not wallet_name or not wallet_name.strip():
        return False, "❌ Wallet name cannot be empty"
    
    if not address or not address.strip():
        return False, "❌ Address cannot be empty"
    
    # Clean inputs
    company = company.strip()
    wallet_name = wallet_name.strip()
    address = address.strip()
    
    # Validate TRC20 address format
    if not validate_trc20_address(address):
        return False, f"❌ Invalid TRC20 address format: {address}\n(Must start with 'T' and be 34 characters)"
    
    # Create wallet key (wallet_name should already include company prefix)
    wallet_key = wallet_name
    
    # Load current wallets
    wallets = load_wallets()
    
    # Check if wallet key already exists
    if wallet_key in wallets:
        return False, f"❌ Wallet '{wallet_key}' already exists"

    # Check if address is already used
    for existing_key, wallet_info in wallets.items():
        if wallet_info.get('address') == address:
            return False, f"❌ Address already used by '{existing_key}'"
    
    # Test the address by fetching balance
    try:
        from bot.usdt_checker import get_usdt_trc20_balance
        
        balance = get_usdt_trc20_balance(address)
        if balance is None:
            return False, "❌ Unable to fetch balance for address (invalid or API error)"
    except Exception as e:
        return False, f"❌ Error testing address: {str(e)}"
    
    # Add new wallet
    wallets[wallet_key] = {
        "company": company,
        "wallet": wallet_name,
        "address": address
    }
    
    # Save to file
    if not save_wallets(wallets):
        return False, "❌ Failed to save wallet to file"
    
    # Success message - formatted for Telegram
    message = f"""✅ *Wallet Added Successfully*

📋 *Details:*
• Company: {company}
• Wallet: {wallet_name}
• Address: `{address[:10]}...{address[-6:]}`
• Current Balance: {balance:,.2f} USDT

📊 *Total Wallets:* {len(wallets)}"""
    
    return True, message


def remove_wallet(wallet_key: str) -> Tuple[bool, str]:
    """
    Remove a wallet from storage.
    
    Args:
        wallet_key: Full wallet key (e.g., "KZP TH BM 1")
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not wallet_key or not wallet_key.strip():
        return False, "❌ Wallet key cannot be empty"
    
    wallet_key = wallet_key.strip()
    
    # Load current wallets
    wallets = load_wallets()
    
    # Check if wallet exists
    if wallet_key not in wallets:
        return False, f"❌ Wallet '{wallet_key}' not found"
    
    # Get wallet info before removing
    wallet_info = wallets[wallet_key]
    address = wallet_info.get('address', 'Unknown')
    
    # Get final balance
    try:
        from bot.usdt_checker import get_usdt_trc20_balance
        
        balance = get_usdt_trc20_balance(address)
        balance_text = f"{balance:,.2f} USDT" if balance is not None else "Unable to fetch"
    except:
        balance_text = "Unable to fetch"
    
    # Remove wallet
    del wallets[wallet_key]
    
    # Save to file
    if not save_wallets(wallets):
        # Rollback on save failure
        wallets[wallet_key] = wallet_info
        return False, "❌ Failed to save changes to file"
    
    # Success message - formatted for Telegram
    message = f"""✅ *Wallet Removed Successfully*

📋 *Removed:*
• Wallet: {wallet_key}
• Address: `{address[:10]}...{address[-6:]}`
• Final Balance: {balance_text}

📊 *Remaining Wallets:* {len(wallets)}"""
    
    return True, message


def list_wallets() -> Tuple[bool, str]:
    """
    List all current wallets.
    
    Returns:
        Tuple[bool, str]: (success, formatted_list)
    """
    wallets = load_wallets()
    
    if not wallets:
        return False, "❌ No wallets configured\n\nUse `/add \"company\" \"wallet\" \"address\"` to add wallets"
    
    # Group by company
    companies = {}
    for wallet_key, wallet_info in wallets.items():
        company = wallet_info.get('company', 'Unknown')
        if company not in companies:
            companies[company] = []
        companies[company].append((wallet_key, wallet_info))
    
    # Format output for Telegram
    lines = []
    
    for company, wallet_list in companies.items():
        lines.append(f"*{company}:*")
        for wallet_key, wallet_info in wallet_list:
            address = wallet_info.get('address', 'Unknown')
            lines.append(f"• *{wallet_key}*: `{address}`")
        lines.append("")  # Empty line between companies
    
    lines.append(f"*Total Wallets:* {len(wallets)}")
    
    return True, "\n".join(lines)