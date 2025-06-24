# 🤖 Telegram Crypto Wallet Monitor Bot

A smart Telegram bot that automatically tracks USDT (TRC20) wallet balances and sends daily reports to your team. Perfect for businesses managing multiple crypto wallets across different locations.

## ✨ Features

**🔄 Automatic Monitoring**: Checks your USDT wallet balances 24/7 and sends daily summary reports  
**⚡ Real-Time Commands**: Check balance updates anytime with simple commands  
**🔒 Secure & Private**: Only authorized team members can use wallet commands  
**👥 Team Collaboration**: Works in Telegram groups for shared visibility  

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token ([create here](https://t.me/BotFather))
- Telegram Group Chat ID
- Team member Telegram user IDs

### Installation

1. **Clone and setup**
   ```bash
   git clone <your-repo-url>
   cd telegram-crypto-bot
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Add your wallets**
   ```bash
   # Edit wallets.json or use /add command
   ```

4. **Start the bot**
   ```bash
   python telegram_bot.py
   ```

## ⚙️ Configuration

Create a `.env` file with your settings:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_group_chat_id_here

# User Authorization (comma-separated user IDs)
AUTHORIZED_USER=123456789,987654321,555444333

# Environment
ENVIRONMENT=PROD
LOG_LEVEL=INFO
```

## 📱 Commands

### Wallet Management
- `/start` - Initialize bot and check connection
- `/help` - Show all available commands and examples
- `/list` - Display all configured wallets
- `/add "company" "wallet_name" "address"` - Add new wallet
- `/remove "wallet_name"` - Remove wallet from monitoring

### Balance Checking
- `/check` - Check all wallet balances
- `/check "wallet_name"` - Check specific wallet
- `/check "TRC20_address"` - Check by address
- `/check "wallet1" "wallet2"` - Check multiple wallets

### Examples
```
/add "KZP" "Main Store" "TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS"
/remove "Main Store"
/check "Main Store"
/check "TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS"
```

## 📊 Daily Reports

The bot automatically sends daily balance reports at **12:00 AM GMT+7** to your configured group.

### Setup Daily Reports
```bash
# Start the daily report scheduler
./start_daily_reports.sh

# Test immediate report
python main.py test

# Monitor logs
tail -f daily_reports.log
```

### Sample Daily Report
```
💰 Daily Balance Report

⏰ Time: 2025-06-24 00:00 GMT+7

• KZP Store 1: 50,000.00 USDT
• KZP Store 2: 25,000.00 USDT
• KZP Office: 10,000.00 USDT

📊 Total: 85,000.00 USDT
```

## 🏗️ File Structure

```
telegram-crypto-bot/
├── bot/
│   ├── handlers/           # Command handlers
│   ├── services/           # Business logic
│   └── utils/             # Configuration & utilities
├── main.py                # Daily report scheduler
├── telegram_bot.py        # Interactive bot
├── wallets.json          # Wallet configuration
└── .env                  # Your configuration
```

## 🔐 Security Features

- **User Authorization**: Only pre-approved team members can use commands
- **Group Restrictions**: Bot only works in your designated group
- **Read-Only Access**: Bot only reads wallet balances, cannot make transactions
- **Secure Configuration**: Supports environment-based credential management

## 📋 Wallet Format

The bot works with **USDT TRC20** wallets only. Addresses must:
- Start with 'T'
- Be exactly 34 characters long
- Example: `TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS`

### Wallet Storage Format
```json
{
  "Wallet Name": {
    "company": "Company Name",
    "wallet": "Wallet Name",
    "address": "TRC20_Address_Here"
  }
}
```

## 🔧 Maintenance

### Check Status
```bash
# Check if bot is running
ps aux | grep telegram_bot

# View recent logs
tail -f telegram_bot.log
tail -f daily_reports.log

# Check wallet count
python -c "import json; print(f'Wallets: {len(json.load(open(\"wallets.json\")))}')"
```

### Restart Services
```bash
# Restart interactive bot
python telegram_bot.py  # Auto-kills old instances

# Restart daily reports
./start_daily_reports.sh
```

### Backup Important Files
```bash
# Backup wallet configuration
cp wallets.json wallets.json.backup

# Backup environment settings
cp .env .env.backup
```

## 🐛 Troubleshooting

**Bot not responding?**
- Check if it's running: `ps aux | grep telegram_bot`
- Check logs: `tail -f telegram_bot.log`
- Restart: `python telegram_bot.py`

**Daily reports not working?**
- Check scheduler: `ps aux | grep main.py`
- Test manually: `python main.py test`
- Check logs: `tail -f daily_reports.log`

**Permission errors?**
- Verify your user ID is in `AUTHORIZED_USER`
- Check group chat ID is correct
- Ensure bot has send message permissions in group

**Commands not working?**
- All arguments must be in quotes: `/check "wallet name"`
- Use `/list` to see exact wallet names
- Check wallet addresses are valid TRC20 format

## 📈 Monitoring & Logs

### Log Files
- `telegram_bot.log` - Interactive bot logs
- `daily_reports.log` - Scheduled report logs

### Key Metrics to Monitor
- Daily report delivery success rate
- API response times for balance checks
- Wallet count and total portfolio value
- User command usage patterns

## 🤝 Team Setup

1. **Create Telegram group** for your team
2. **Add the bot** to the group
3. **Get group chat ID** using provided scripts
4. **Add team member user IDs** to `.env`
5. **Test all commands** work for authorized users
6. **Verify daily reports** are delivered to group

## 📞 Support

- Use `/help` in Telegram for command reference
- Check logs for error details
- Verify wallet addresses are valid TRC20
- Ensure environment configuration is correct

---

**Built for reliable crypto portfolio monitoring with enterprise-grade security and team collaboration features.**