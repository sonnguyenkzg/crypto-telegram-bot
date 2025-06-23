#!/bin/bash
"""
Startup script for daily report scheduler
Safely starts the scheduler with proper process management
"""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Daily Report Scheduler..."

# Kill any existing scheduler processes
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Start the scheduler in background
echo "⏰ Starting daily report scheduler (GMT+7 midnight)..."
nohup python main.py > daily_reports.log 2>&1 &

echo "✅ Daily report scheduler started!"
echo "📋 Process ID: $!"
echo "📄 Logs: daily_reports.log"
echo ""
echo "Commands:"
echo "  View logs: tail -f daily_reports.log"
echo "  Test report: python main.py test"
echo "  Stop scheduler: pkill -f 'python.*main.py'"
echo ""