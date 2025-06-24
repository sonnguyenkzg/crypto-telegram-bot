# 🧪 UAT Testing Guide

Complete User Acceptance Testing guide for the Telegram Crypto Wallet Monitor Bot. Follow this guide to ensure all features work correctly before production deployment.

## 📋 Testing Overview

**Environment**: Test in your Telegram group  
**Duration**: 30-45 minutes  
**Requirements**: Bot running, group configured, test wallet data  

---

## 🔐 1. Authorization Testing

### Test 1.1: Authorized User Access
**Command**: `/start`  
**Expected Result**:
```
🤖 Crypto Wallet Monitor Bot is running!

Hello [Your Name]! 👋

This bot helps you monitor USDT wallet balances.

Environment: PROD
Status: ✅ Connected and Ready

Try /help to see available commands.
```

**✅ Pass Criteria**: Welcome message with your name and environment info

### Test 1.2: Unauthorized User Blocked
**Setup**: Temporarily remove your user ID from `AUTHORIZED_USER` in `.env`  
**Command**: `/start`  
**Expected Result**:
```
❌ You are not authorized to use this bot.
```

**✅ Pass Criteria**: Clear rejection message, no wallet access  
**Cleanup**: Restore your user ID to `.env`

---

## 🚀 2. Basic Command Testing

### Test 2.1: Help Command
**Command**: `/help`  
**Expected Result**: Comprehensive help with:
- All available commands listed
- Usage examples for each command
- Notes about quote requirements
- TRC20 address format info

**✅ Pass Criteria**: Complete command list with examples

### Test 2.2: List Wallets
**Command**: `/list`  
**Expected Result**:
```
📋 Configured Wallets (X total)

🏢 KZP
  • KZP 96G1: `TNZj5wTSMK4oR79CYzy8BGK6LWNmQxcuM8`
  • KZP BLG1: `TARvAP993BSFBuQhjc8oG4gviskNDftB7Z`
  [... more wallets]

💡 Use /check to see current balances
```

**✅ Pass Criteria**: All wallets displayed, grouped by company, full addresses shown

---

## 📊 3. Balance Checking Testing

### Test 3.1: Check All Wallets
**Command**: `/check`  
**Expected Result**:
```
🤖 Wallet Balance Check

⏰ Time: 2025-06-24 XX:XX GMT+7

• KZP 96G1: X,XXX.XX USDT
• KZP BLG1: X,XXX.XX USDT
[... all wallets]

📊 Total: XXX,XXX.XX USDT
```

**✅ Pass Criteria**: 
- Shows "🔄 Checking balances..." message first
- Displays all wallets with real balances
- Correct GMT+7 timestamp
- Accurate total calculation

### Test 3.2: Check Single Wallet by Name
**Command**: `/check "KZP 96G1"`  
**Expected Result**:
```
🤖 Wallet Balance Check

⏰ Time: 2025-06-24 XX:XX GMT+7

• KZP 96G1: X,XXX.XX USDT
```

**✅ Pass Criteria**: Shows only requested wallet with balance

### Test 3.3: Check by TRC20 Address (Case Insensitive)
**Command**: `/check "TNZj5wTSMK4oR79CYzy8BGK6LWNmQxcuM8"`  
**Command**: `/check "TNZJ5WTSMK4OR79CYZY8BGK6LWNMQXCUM8"`  
**Expected Result**: Both commands should work and show "KZP 96G1" balance

**✅ Pass Criteria**: Case-insensitive address matching works

### Test 3.4: Check Multiple Wallets
**Command**: `/check "KZP 96G1" "KZP BLG1"`  
**Expected Result**:
```
🤖 Wallet Balance Check

⏰ Time: 2025-06-24 XX:XX GMT+7

• KZP 96G1: X,XXX.XX USDT
• KZP BLG1: X,XXX.XX USDT

📊 Total: X,XXX.XX USDT
```

**✅ Pass Criteria**: Shows only requested wallets with total

### Test 3.5: Mixed Valid/Invalid Wallets
**Command**: `/check "KZP 96G1" "NONEXISTENT"`  
**Expected Result**:
```
🤖 Wallet Balance Check

⏰ Time: 2025-06-24 XX:XX GMT+7

• KZP 96G1: X,XXX.XX USDT

📊 Total: X,XXX.XX USDT
❌ Not found: NONEXISTENT
```

**✅ Pass Criteria**: Shows valid wallet + lists invalid ones

---

## ➕ 4. Add Wallet Testing

### Test 4.1: Successful Wallet Addition
**Command**: `/add "TEST" "Test Wallet" "TTestAddress123456789012345678901234"`  
**Expected Result**:
```
✅ Wallet Added Successfully

📋 Details:
• Company: TEST
• Wallet: Test Wallet
• Address: TTestAddress123456789012345678901234

Use /check to see current balance.
```

**✅ Pass Criteria**: Success confirmation with wallet details

### Test 4.2: Missing Arguments Error
**Command**: `/add`  
**Expected Result**:
```
❌ Missing arguments

Usage: `/add "company" "wallet_name" "address"`
Example: `/add "KZP" "KZP WDB2" "TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS"`
```

**✅ Pass Criteria**: Clear error with usage instructions

### Test 4.3: Missing Quotes Error
**Command**: `/add TEST WALLET TADDRESS`  
**Expected Result**:
```
❌ Expected 3 quoted arguments, found 0

Usage: `/add "company" "wallet_name" "address"`
Example: `/add "KZP" "KZP WDB2" "TEhmKXCPgX64yjQ3t9skuSyUQBxwaWY4KS"`
```

**✅ Pass Criteria**: Specific error about quote requirement

### Test 4.4: Invalid TRC20 Address
**Command**: `/add "TEST" "Test Wallet" "InvalidAddress"`  
**Expected Result**:
```
❌ Invalid TRC20 address. Address must start with 'T' and be 34 characters long.
```

**✅ Pass Criteria**: Clear TRC20 format validation error

### Test 4.5: Duplicate Wallet Name
**Command**: `/add "TEST" "Test Wallet" "TAnotherValidAddress12345678901234"`  
**Expected Result**:
```
❌ Wallet 'Test Wallet' already exists.
```

**✅ Pass Criteria**: Prevents duplicate wallet names

---

## ➖ 5. Remove Wallet Testing

### Test 5.1: Successful Wallet Removal
**Command**: `/remove "Test Wallet"`  
**Expected Result**:
```
✅ Wallet Removed Successfully

Wallet: Test Wallet
Company: TEST

The wallet has been removed from monitoring.
Use /list to see remaining wallets.
```

**✅ Pass Criteria**: Success confirmation with details

### Test 5.2: Wallet Not Found with Suggestions
**Command**: `/remove "Nonexistent"`  
**Expected Result**:
```
❌ Wallet Nonexistent not found

💡 Did you mean: `KZP 96G1`, `KZP BLG1`

📋 Use `/list` to see all available wallets
```

**✅ Pass Criteria**: Error with helpful suggestions

### Test 5.3: Missing Quotes Error
**Command**: `/remove Test Wallet`  
**Expected Result**:
```
❌ Expected 1 quoted argument, found 2

Usage: `/remove "wallet_name"`
Example: `/remove "KZP TEST1"`

💡 Use `/list` to see available wallets
```

**✅ Pass Criteria**: Clear quote requirement error

---

## ❌ 6. Error Handling Testing

### Test 6.1: Unquoted Check Command
**Command**: `/check KZP 96G1`  
**Expected Result**:
```
❌ No valid wallet names or addresses found in: `KZP 96G1`

Note: All wallet names and addresses must be in quotes!

Usage:
• `/check` - Check all wallets
• `/check "wallet_name"` - Check by wallet name
[... more usage info]
```

**✅ Pass Criteria**: Clear error about quote requirement

### Test 6.2: Unknown Commands
**Command**: `/status`  
**Command**: `/balance`  
**Expected Result**:
```
❌ Unknown command: `/status`

💡 Available commands:
• `/start` - Start the bot
• `/help` - Show all commands
• `/list` - Show wallets
• `/check` - Check balances
• `/add` - Add wallet
• `/remove` - Remove wallet

Use `/help` for detailed usage information.
```

**✅ Pass Criteria**: Helpful error with available commands

### Test 6.3: Empty Quoted Arguments
**Command**: `/check ""`  
**Expected Result**: Appropriate error message about empty arguments

**✅ Pass Criteria**: Handles empty quotes gracefully

---

## 📅 7. Daily Reports Testing

### Test 7.1: Manual Test Report
**Command**: `python main.py test` (in terminal)  
**Expected Result**: Daily report sent to group with:
- Current timestamp in GMT+7
- All wallet balances
- Total calculation
- Same format as `/check` output

**✅ Pass Criteria**: Report delivered to group successfully

### Test 7.2: 30-Second Test Reports
**Command**: `python test_daily_reports_30s.py` (in terminal)  
**Expected Result**: 
- Reports sent every 30 seconds
- Clear "TEST REPORT #X" headers
- Real balance data
- Automatic stop after 10 reports

**✅ Pass Criteria**: Multiple test reports delivered successfully

---

## 🌐 8. Network & API Testing

### Test 8.1: API Timeout Handling
**Monitor**: Check logs during balance fetching for any timeout messages  
**Expected**: Graceful handling of API delays, no crashes

**✅ Pass Criteria**: Bot continues working even if some API calls fail

### Test 8.2: External Address Check
**Command**: `/check "TExternalAddress123456789012345678"`  
**Expected Result**: Either shows balance or clear error message

**✅ Pass Criteria**: Handles external addresses correctly

---

## 📊 9. Performance Testing

### Test 9.1: Large Balance Check
**Command**: `/check` (with all wallets)  
**Monitor**: Response time and memory usage  
**Expected**: Completes within reasonable time (< 2 minutes for 10 wallets)

**✅ Pass Criteria**: Acceptable performance with multiple wallets

### Test 9.2: Rapid Commands
**Test**: Send multiple commands quickly  
**Expected**: Bot handles all commands without crashes

**✅ Pass Criteria**: Stable under rapid command usage

---

## ✅ UAT Completion Checklist

Mark each section as complete:

```
□ 🔐 Authorization Testing (2 tests)
□ 🚀 Basic Command Testing (2 tests)  
□ 📊 Balance Checking Testing (5 tests)
□ ➕ Add Wallet Testing (5 tests)
□ ➖ Remove Wallet Testing (3 tests)
□ ❌ Error Handling Testing (3 tests)
□ 📅 Daily Reports Testing (2 tests)
□ 🌐 Network & API Testing (2 tests)
□ 📊 Performance Testing (2 tests)
```

**Total Test Cases**: 26  
**Estimated Time**: 30-45 minutes  

## 🎯 Final Validation

After completing all tests:

1. **✅ All commands work as expected**
2. **✅ Error messages are clear and helpful**
3. **✅ Authorization works correctly**
4. **✅ Daily reports deliver successfully**
5. **✅ Real balance data is accurate**
6. **✅ Performance is acceptable**

**🎉 Ready for Production Deployment!**

---

## 🧹 Post-Testing Cleanup

After UAT completion:

```bash
# Run cleanup script to remove test data
python cleanup_test_data.py

# Verify production readiness
python telegram_bot.py
./start_daily_reports.sh
```

**Your bot is now ready for team deployment!**