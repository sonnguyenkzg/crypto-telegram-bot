#!/usr/bin/env python3
"""
Wallet Manager Module - Phase 2
Handles USDT TRC20 wallet management and balance checking
"""

import json
import csv
import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Tuple
import pytz

logger = logging.getLogger(__name__)

# USDT TRC20 contract address - same as Slack bot
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

class WalletManager:
    def __init__(self, wallets_file: str = "wallets.json", csv_file: str = "wallet_balances.csv"):
        self.wallets_file = wallets_file
        self.csv_file = csv_file
        self.timezone = pytz.timezone('Asia/Bangkok')  # GMT+7
        
        # Ensure files exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize wallet storage files if they don't exist"""
        # Initialize wallets.json
        if not os.path.exists(self.wallets_file):
            with open(self.wallets_file, 'w') as f:
                json.dump({}, f, indent=2)
            logger.info(f"Created {self.wallets_file}")
        
        # Initialize CSV with headers if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'company', 'wallet_name', 'address', 'balance', 'timezone'])
            logger.info(f"Created {self.csv_file}")
    
    def load_wallets(self) -> Dict:
        """Load wallets from JSON file"""
        try:
            with open(self.wallets_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load wallets: {e}")
            return {}
    
    def save_wallets(self, wallets: Dict):
        """Save wallets to JSON file"""
        try:
            with open(self.wallets_file, 'w') as f:
                json.dump(wallets, f, indent=2)
            logger.info("Wallets saved successfully")
        except Exception as e:
            logger.error(f"Failed to save wallets: {e}")
            raise
    
    def add_wallet(self, company: str, wallet_name: str, address: str) -> Tuple[bool, str]:
        """Add a new wallet"""
        # Validate TRC20 address
        if not self._is_valid_trc20_address(address):
            return False, "❌ Invalid TRC20 address. Address must start with 'T' and be 34 characters long."
        
        wallets = self.load_wallets()
        
        # Check if wallet name already exists
        if wallet_name in wallets:
            return False, f"❌ Wallet '{wallet_name}' already exists."
        
        # Add wallet
        wallets[wallet_name] = {
            "company": company,
            "address": address,
            "added_date": datetime.now(self.timezone).isoformat()
        }
        
        try:
            self.save_wallets(wallets)
            logger.info(f"Added wallet: {company} - {wallet_name} - {address}")
            return True, f"✅ Wallet '{wallet_name}' added successfully!"
        except Exception as e:
            return False, f"❌ Failed to add wallet: {e}"
    
    def remove_wallet(self, wallet_name: str) -> Tuple[bool, str]:
        """Remove a wallet"""
        wallets = self.load_wallets()
        
        if wallet_name not in wallets:
            return False, f"❌ Wallet '{wallet_name}' not found."
        
        # Remove wallet
        removed_wallet = wallets.pop(wallet_name)
        
        try:
            self.save_wallets(wallets)
            logger.info(f"Removed wallet: {wallet_name}")
            return True, f"✅ Wallet '{wallet_name}' ({removed_wallet['company']}) removed successfully!"
        except Exception as e:
            return False, f"❌ Failed to remove wallet: {e}"
    
    def list_wallets(self) -> str:
        """List all wallets"""
        wallets = self.load_wallets()
        
        if not wallets:
            return "📋 No wallets configured.\n\nUse `/add Company WalletName Address` to add your first wallet."
        
        wallet_list = "📋 *Configured Wallets:*\n\n"
        for name, info in wallets.items():
            wallet_list += f"• *{name}* ({info['company']})\n"
            wallet_list += f"  `{info['address']}`\n\n"
        
        wallet_list += f"*Total wallets:* {len(wallets)}"
        return wallet_list
    
    def _is_valid_trc20_address(self, address: str) -> bool:
        """Validate TRC20 address format"""
        return address.startswith('T') and len(address) == 34 and address.isalnum()
    
    async def get_wallet_balance(self, address: str) -> Tuple[bool, Decimal]:
        """Get USDT TRC20 balance for a wallet address - using exact same API as Slack bot"""
        try:
            # Using EXACT same endpoint and format as your Slack bot
            url = f"https://apilist.tronscanapi.com/api/account/tokens?address={address}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        json_data = await response.json()
                        data = json_data.get("data", [])
                        
                        if not data:
                            logger.warning(f"No token data found for address {address}")
                            return True, Decimal('0.0')
                        
                        # Look for USDT token using exact same logic as Slack bot
                        for token in data:
                            if token.get("tokenId") == USDT_CONTRACT:
                                raw_balance_str = token.get("balance", "0")
                                try:
                                    raw_balance = Decimal(raw_balance_str)
                                except Exception as e:
                                    logger.error(f"Error converting balance '{raw_balance_str}' for {address}: {e}")
                                    return True, Decimal('0.0')
                                
                                # USDT TRC20 has 6 decimal places (1,000,000 sun per USDT) - exact same as Slack bot
                                balance = raw_balance / Decimal('1000000')
                                return True, balance
                        
                        # USDT token not found for this address - same as Slack bot
                        return True, Decimal('0.0')
                    else:
                        logger.error(f"API request failed: {response.status}")
                        return False, Decimal('0.0')
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout while checking balance for {address}")
            return False, Decimal('0.0')
        except Exception as e:
            logger.error(f"Error checking balance for {address}: {e}")
            return False, Decimal('0.0')
    
    async def check_wallet_balance(self, wallet_name: str = None) -> str:
        """Check balance for specific wallet or all wallets"""
        wallets = self.load_wallets()
        
        if not wallets:
            return "❌ No wallets configured. Use `/add` to add wallets first."
        
        if wallet_name:
            # Check specific wallet
            if wallet_name not in wallets:
                return f"❌ Wallet '{wallet_name}' not found. Use `/list` to see available wallets."
            
            wallet_info = wallets[wallet_name]
            success, balance = await self.get_wallet_balance(wallet_info['address'])
            
            if success:
                return f"💰 *{wallet_name}* ({wallet_info['company']})\n`{wallet_info['address']}`\n\n*Balance:* {balance:,.2f} USDT"
            else:
                return f"❌ Failed to check balance for '{wallet_name}'. Please try again."
        
        else:
            # Check all wallets
            current_time = datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M GMT+7')
            message = f"💰 *Wallet Balance Report*\n\n⏰ Time: {current_time}\n\n"
            
            total_balance = Decimal('0.00')
            failed_wallets = []
            
            for name, info in wallets.items():
                success, balance = await self.get_wallet_balance(info['address'])
                
                if success:
                    message += f"• *{name}*: {balance:,.2f} USDT\n"
                    total_balance += balance
                    
                    # Log to CSV
                    self._log_balance_to_csv(info['company'], name, info['address'], balance)
                else:
                    failed_wallets.append(name)
            
            message += f"\n📊 *Total:* {total_balance:,.2f} USDT"
            
            if failed_wallets:
                message += f"\n\n⚠️ Failed to check: {', '.join(failed_wallets)}"
            
            return message
    
    def _log_balance_to_csv(self, company: str, wallet_name: str, address: str, balance: Decimal):
        """Log balance to CSV file"""
        try:
            timestamp = datetime.now(self.timezone).isoformat()
            
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, company, wallet_name, address, float(balance), 'GMT+7'])
            
            logger.debug(f"Logged balance for {wallet_name}: {balance}")
        except Exception as e:
            logger.error(f"Failed to log balance to CSV: {e}")
    
    async def generate_daily_report(self) -> str:
        """Generate daily balance report"""
        logger.info("Generating daily balance report")
        return await self.check_wallet_balance()
    
    def get_wallet_count(self) -> int:
        """Get total number of configured wallets"""
        wallets = self.load_wallets()
        return len(wallets)