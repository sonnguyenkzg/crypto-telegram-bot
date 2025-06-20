# bot/usdt_checker.py
"""
Provides functions to fetch USDT TRC20 wallet balances from the Tronscan API.
Handles API communication, data parsing, and prepares a human-readable summary.
"""
import requests
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from bot.telegram_config import API_TIMEOUT, USDT_CONTRACT, GMT_OFFSET
from bot.wallet_manager import load_wallets


def get_wallets_for_checking():
    """Get wallets in format needed for balance checking"""
    wallet_data = load_wallets()
    # Convert to simple format: {name: address}
    return {name: data['address'] for name, data in wallet_data.items()}


def get_usdt_trc20_balance(address: str) -> Decimal:
    """
    Fetches the USDT TRC20 balance for a given Tron address using the Tronscan API.
    Handles network errors and unexpected API responses.

    Args:
        address (str): The Tron wallet address to query.

    Returns:
        Decimal: The USDT balance as a Decimal object, or Decimal('0.0') on error.
    """
    url = f"https://apilist.tronscanapi.com/api/account/tokens?address={address}"
    
    try:
        resp = requests.get(url, timeout=API_TIMEOUT)
        resp.raise_for_status()

        data = resp.json().get("data", [])
        if not data:
            print(f"Warning: No token data found for address {address}")
            return Decimal('0.0')

        for token in data:
            if token.get("tokenId") == USDT_CONTRACT:
                raw_balance_str = token.get("balance", "0")
                try:
                    raw_balance = Decimal(raw_balance_str)
                except Exception as e:
                    print(f"Error converting balance '{raw_balance_str}' for {address}: {e}")
                    return Decimal('0.0')

                # USDT TRC20 has 6 decimal places (1,000,000 sun per USDT)
                return raw_balance / Decimal('1000000')
        
        # USDT token not found for this address
        return Decimal('0.0')

    except requests.exceptions.Timeout:
        print(f"Error fetching balance for {address}: Request timed out")
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching balance for {address}: HTTP error {e.response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Error fetching balance for {address}: Connection error")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching balance for {address}: Request error: {e}")
    except ValueError as e:
        print(f"Error decoding JSON for {address}: {e}")
    except Exception as e:
        print(f"Unexpected error fetching balance for {address}: {e}")
    
    return Decimal('0.0')


def fetch_all_usdt_balances() -> tuple[str, dict[str, Decimal]]:
    """
    Fetches USDT balances for all configured wallets.
    Prepares a formatted text summary message and returns the raw balances.

    Returns:
        tuple[str, dict[str, Decimal]]: A tuple containing:
            - str: Human-readable summary message with individual and total balances
            - dict[str, Decimal]: Dictionary mapping wallet names to USDT balances
    """
    wallets = get_wallets_for_checking()
    if not wallets:
        return "❌ No wallets configured", {}
    
    # Fetch balances for each wallet
    balances = {name: get_usdt_trc20_balance(addr) for name, addr in wallets.items()}
    
    # Calculate total balance
    total = sum(balances.values())

    # Get current time in GMT+7
    gmt_now = datetime.now(timezone(timedelta(hours=GMT_OFFSET)))
    time_str = gmt_now.strftime("%Y-%m-%d %H:%M")

    # Build message - formatted for Telegram
    lines = [
        f"💵 *USDT TRC20 Wallet Balances* 💵",
        f"_As of {time_str} GMT+{GMT_OFFSET}_",
        ""
    ]

    for name, value in balances.items():
        lines.append(f"• *{name}*: *{value:,.2f} USDT*")
    
    lines.append("")
    lines.append(f"➕ *Total*: *{total:,.2f} USDT*")

    return "\n".join(lines), balances