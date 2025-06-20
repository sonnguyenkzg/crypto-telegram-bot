#!/bin/bash
# start_telegram_bot.sh - Startup script for Telegram Crypto Bot

set -e

echo "🚀 Starting Telegram Crypto Wallet Monitor Bot..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your bot configuration."
    echo "Use the .env.template as a reference."
    exit 1
fi

# Stop any existing bot processes
echo "Stopping any existing bot processes..."
pkill -f "telegram_bot.py" || true

# Wait a moment for processes to stop
sleep 2

# Start the bot
echo "Starting bot..."
nohup python telegram_bot.py > telegram_bot.log 2>&1 &

# Get the process ID
BOT_PID=$!
echo "Bot started with PID: $BOT_PID"

# Wait a moment and check if bot is still running
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running successfully!"
    echo "📋 Check logs: tail -f telegram_bot.log"
    echo "🛑 Stop bot: pkill -f telegram_bot.py"
else
    echo "❌ Bot failed to start. Check the logs:"
    cat telegram_bot.log
    exit 1
fi