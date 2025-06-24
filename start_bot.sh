#!/bin/bash
"""
Unified Bot Startup Script
Starts both interactive bot and daily reports together
"""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 ======= TELEGRAM CRYPTO BOT STARTUP =======${NC}"
echo "📅 $(date)"
echo "🖥️  Server: $(hostname)"
echo "👤 User: $(whoami)"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "telegram_bot.py" ] || [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: Must run from telegram-crypto-bot directory${NC}"
    echo "📁 Current directory: $(pwd)"
    echo "💡 Expected files: telegram_bot.py, main.py"
    exit 1
fi

# Function to check if process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        return 0  # Process running
    else
        return 1  # Process not running
    fi
}

# Stop existing processes
stop_existing() {
    echo -e "${YELLOW}🛑 Stopping existing bot processes...${NC}"
    
    if check_process "telegram_bot.py"; then
        echo "   Stopping telegram_bot.py..."
        pkill -f "telegram_bot.py"
        sleep 2
    fi
    
    if check_process "python.*main.py"; then
        echo "   Stopping daily reports..."
        pkill -f "python.*main.py"
        sleep 2
    fi
    
    echo -e "${GREEN}   ✅ Cleanup completed${NC}"
}

# Activate virtual environment
setup_environment() {
    echo -e "${BLUE}📦 Setting up environment...${NC}"
    
    if [ -d ".venv" ]; then
        echo "   Activating virtual environment..."
        source .venv/bin/activate
        echo -e "${GREEN}   ✅ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Virtual environment not found, using system Python${NC}"
    fi
}

# Validate configuration
validate_config() {
    echo -e "${BLUE}🔍 Validating configuration...${NC}"
    
    # Check .env file
    if [ ! -f ".env" ]; then
        echo -e "${RED}   ❌ .env file not found${NC}"
        exit 1
    fi
    
    # Check wallets.json
    if [ ! -f "wallets.json" ]; then
        echo -e "${RED}   ❌ wallets.json not found${NC}"
        exit 1
    fi
    
    # Test configuration loading
    if python -c "from bot.utils.config import Config; Config.validate_config()" 2>/dev/null; then
        echo -e "${GREEN}   ✅ Configuration valid${NC}"
    else
        echo -e "${RED}   ❌ Configuration validation failed${NC}"
        echo "   💡 Check your .env file settings"
        exit 1
    fi
}

# Start interactive bot
start_interactive_bot() {
    echo -e "${BLUE}🎮 Starting interactive bot...${NC}"
    
    # Start telegram_bot.py in background
    nohup python telegram_bot.py > telegram_bot.log 2>&1 &
    TELEGRAM_BOT_PID=$!
    
    # Wait a moment and check if it started successfully
    sleep 3
    
    if check_process "telegram_bot.py"; then
        echo -e "${GREEN}   ✅ Interactive bot started (PID: $TELEGRAM_BOT_PID)${NC}"
        echo "   📄 Logs: telegram_bot.log"
        return 0
    else
        echo -e "${RED}   ❌ Failed to start interactive bot${NC}"
        echo "   💡 Check logs: tail -f telegram_bot.log"
        return 1
    fi
}

# Start daily reports
start_daily_reports() {
    echo -e "${BLUE}📅 Starting daily reports...${NC}"
    
    # Start main.py in background
    nohup python main.py > daily_reports.log 2>&1 &
    DAILY_REPORTS_PID=$!
    
    # Wait a moment and check if it started successfully
    sleep 3
    
    if check_process "python.*main.py"; then
        echo -e "${GREEN}   ✅ Daily reports started (PID: $DAILY_REPORTS_PID)${NC}"
        echo "   📄 Logs: daily_reports.log"
        echo "   ⏰ Scheduled: Daily reports at 00:00 GMT+7"
        return 0
    else
        echo -e "${RED}   ❌ Failed to start daily reports${NC}"
        echo "   💡 Check logs: tail -f daily_reports.log"
        return 1
    fi
}

# Show status
show_status() {
    echo ""
    echo -e "${GREEN}🎉 ======= STARTUP COMPLETED =======${NC}"
    echo ""
    echo "📊 Services Status:"
    
    if check_process "telegram_bot.py"; then
        echo -e "   ${GREEN}✅ Interactive Bot: Running${NC}"
    else
        echo -e "   ${RED}❌ Interactive Bot: Not Running${NC}"
    fi
    
    if check_process "python.*main.py"; then
        echo -e "   ${GREEN}✅ Daily Reports: Running${NC}"
    else
        echo -e "   ${RED}❌ Daily Reports: Not Running${NC}"
    fi
    
    echo ""
    echo "📋 Management Commands:"
    echo "   View logs:       tail -f telegram_bot.log daily_reports.log"
    echo "   Check processes: ps aux | grep python"
    echo "   Stop all:        pkill -f 'python.*telegram_bot.py|python.*main.py'"
    echo "   Test report:     python main.py test"
    echo ""
    echo "🎯 Bot Features Available:"
    echo "   • Interactive commands in Telegram group"
    echo "   • Daily balance reports at midnight GMT+7"
    echo "   • Real-time wallet monitoring"
    echo ""
}

# Test services
test_services() {
    echo -e "${BLUE}🧪 Testing services...${NC}"
    
    # Test imports
    if python -c "import telegram_bot" 2>/dev/null; then
        echo -e "${GREEN}   ✅ Interactive bot imports successfully${NC}"
    else
        echo -e "${RED}   ❌ Interactive bot import failed${NC}"
        return 1
    fi
    
    if python -c "import main" 2>/dev/null; then
        echo -e "${GREEN}   ✅ Daily reports imports successfully${NC}"
    else
        echo -e "${RED}   ❌ Daily reports import failed${NC}"
        return 1
    fi
    
    echo -e "${GREEN}   ✅ All service tests passed${NC}"
    return 0
}

# Main execution
main() {
    # Pre-startup checks
    stop_existing
    setup_environment
    validate_config
    test_services
    
    echo ""
    echo -e "${BLUE}🚀 Starting services...${NC}"
    echo ""
    
    # Start services
    if start_interactive_bot && start_daily_reports; then
        show_status
        
        echo -e "${GREEN}✨ All services started successfully!${NC}"
        echo ""
        echo "💡 Next steps:"
        echo "   1. Test bot in Telegram: /start"
        echo "   2. Test daily report: python main.py test"
        echo "   3. Monitor logs for any issues"
        echo ""
        
        return 0
    else
        echo -e "${RED}❌ Service startup failed!${NC}"
        echo ""
        echo "🔧 Troubleshooting:"
        echo "   • Check logs: tail -f telegram_bot.log daily_reports.log"
        echo "   • Verify configuration: cat .env"
        echo "   • Test manually: python telegram_bot.py"
        echo ""
        
        return 1
    fi
}

# Handle command line arguments
case "$1" in
    "stop")
        echo -e "${YELLOW}🛑 Stopping all bot services...${NC}"
        stop_existing
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;
    "status")
        echo -e "${BLUE}📊 Service Status:${NC}"
        if check_process "telegram_bot.py"; then
            echo -e "   ${GREEN}✅ Interactive Bot: Running${NC}"
        else
            echo -e "   ${RED}❌ Interactive Bot: Not Running${NC}"
        fi
        if check_process "python.*main.py"; then
            echo -e "   ${GREEN}✅ Daily Reports: Running${NC}"
        else
            echo -e "   ${RED}❌ Daily Reports: Not Running${NC}"
        fi
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting all services...${NC}"
        stop_existing
        sleep 2
        main
        ;;
    "logs")
        echo -e "${BLUE}📄 Showing recent logs...${NC}"
        echo ""
        echo "=== Interactive Bot Logs ==="
        tail -20 telegram_bot.log 2>/dev/null || echo "No telegram_bot.log found"
        echo ""
        echo "=== Daily Reports Logs ==="
        tail -20 daily_reports.log 2>/dev/null || echo "No daily_reports.log found"
        ;;
    "help"|"-h"|"--help")
        echo "Telegram Crypto Bot Startup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "   (no args)    Start all services"
        echo "   stop         Stop all services"
        echo "   restart      Restart all services"  
        echo "   status       Show service status"
        echo "   logs         Show recent logs"
        echo "   help         Show this help"
        echo ""
        ;;
    "")
        # No arguments - start services
        main
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac