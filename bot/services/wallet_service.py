"""
Wallet management service for crypto wallet monitoring.
Handles wallet data persistence and operations.
"""

import json
import os
import logging
from typing import Dict, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class WalletService:
    """Service for managing wallet data operations."""
    
    def __init__(self, wallets_file: str = "wallets.json"):
        self.wallets_file = wallets_file
    
    def load_wallets(self) -> Dict[str, Any]:
        """
        Load wallet data from JSON file.
        
        Returns:
            Dict[str, Any]: Dictionary of wallet data, empty if file doesn't exist
        """
        try:
            if os.path.exists(self.wallets_file):
                with open(self.wallets_file, 'r', encoding='utf-8') as f:
                    wallets = json.load(f)
                    logger.info(f"Loaded {len(wallets)} wallets from {self.wallets_file}")
                    return wallets
            else:
                logger.info(f"Wallets file {self.wallets_file} not found, returning empty dict")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.wallets_file}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading wallets from {self.wallets_file}: {e}")
            return {}
    
    def save_wallets(self, wallets: Dict[str, Any]) -> bool:
        """
        Save wallet data to JSON file.
        
        Args:
            wallets: Dictionary of wallet data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.wallets_file, 'w', encoding='utf-8') as f:
                json.dump(wallets, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(wallets)} wallets to {self.wallets_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving wallets to {self.wallets_file}: {e}")
            return False
    
    def list_wallets(self) -> Tuple[bool, str]:
        """
        List all configured wallets with their details.
        
        Returns:
            Tuple[bool, str]: (success, formatted_message)
        """
        wallets = self.load_wallets()
        
        if not wallets:
            return True, "❌ No wallets configured\n\nUse `/add` to add your first wallet."
        
        # Group wallets by company
        companies = {}
        for wallet_name, wallet_info in wallets.items():
            company = wallet_info.get('company', 'Unknown')
            if company not in companies:
                companies[company] = []
            companies[company].append({
                'name': wallet_name,
                'address': wallet_info.get('address', 'Unknown')
            })
        
        # Build formatted message
        lines = [f"📋 *Configured Wallets* ({len(wallets)} total)\n"]
        
        for company, company_wallets in sorted(companies.items()):
            lines.append(f"🏢 *{company}*")
            for wallet in company_wallets:
                address = wallet['address']
                # Show full address without masking
                lines.append(f"  • *{wallet['name']}*: `{address}`")
            lines.append("")  # Empty line between companies
        
        lines.append("💡 Use /check to see current balances")
        
        return True, "\n".join(lines)
    
    def validate_trc20_address(self, address: str) -> bool:
        """
        Validate if an address is a valid TRC20 address.
        
        Args:
            address: The address to validate
            
        Returns:
            bool: True if valid TRC20 address, False otherwise
        """
        if not address or not isinstance(address, str):
            return False
        
        # TRC20 addresses start with 'T' and are 34 characters long
        return address.startswith('T') and len(address) == 34
    
    def wallet_exists(self, wallet_name: str) -> bool:
        """
        Check if a wallet with the given name already exists.
        
        Args:
            wallet_name: Name of the wallet to check
            
        Returns:
            bool: True if wallet exists, False otherwise
        """
        wallets = self.load_wallets()
        return wallet_name in wallets
    
    def add_wallet(self, company: str, wallet_name: str, address: str) -> Tuple[bool, str]:
        """
        Add a new wallet to the configuration.
        
        Args:
            company: Company name
            wallet_name: Wallet name (must be unique)
            address: TRC20 wallet address
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Validate address
        if not self.validate_trc20_address(address):
            return False, "❌ Invalid TRC20 address. Address must start with 'T' and be 34 characters long."
        
        # Load existing wallets
        wallets = self.load_wallets()
        
        # Check if wallet name already exists
        if wallet_name in wallets:
            return False, f"❌ Wallet '{wallet_name}' already exists."
        
        # Check if address already exists
        for existing_name, existing_info in wallets.items():
            if existing_info.get('address') == address:
                return False, f"❌ Address already exists for wallet '{existing_name}'."
        
        # Add new wallet
        wallets[wallet_name] = {
            "company": company,
            "wallet": wallet_name,
            "address": address
        }
        
        # Save to file
        if self.save_wallets(wallets):
            return True, f"✅ Wallet '{wallet_name}' added successfully."
        else:
            return False, "❌ Failed to save wallet to file."
    
    def remove_wallet(self, wallet_name: str) -> Tuple[bool, str]:
        """
        Remove a wallet from the configuration.
        
        Args:
            wallet_name: Name of the wallet to remove
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Load existing wallets
        wallets = self.load_wallets()
        
        # Check if wallet exists
        if wallet_name not in wallets:
            return False, f"❌ Wallet '{wallet_name}' not found."
        
        # Remove wallet
        removed_wallet = wallets.pop(wallet_name)
        
        # Save to file
        if self.save_wallets(wallets):
            return True, f"✅ Wallet '{wallet_name}' removed successfully."
        else:
            # Restore wallet if save failed
            wallets[wallet_name] = removed_wallet
            return False, "❌ Failed to save changes to file."
    
    def get_wallet_by_name(self, wallet_name: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet information by name.
        
        Args:
            wallet_name: Name of the wallet
            
        Returns:
            Optional[Dict[str, Any]]: Wallet info if found, None otherwise
        """
        wallets = self.load_wallets()
        return wallets.get(wallet_name)
    
    def get_all_addresses(self) -> Dict[str, str]:
        """
        Get all wallet addresses keyed by wallet name.
        
        Returns:
            Dict[str, str]: Dictionary mapping wallet names to addresses
        """
        wallets = self.load_wallets()
        return {name: info.get('address', '') for name, info in wallets.items()}