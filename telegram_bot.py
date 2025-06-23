#!/usr/bin/env python3
"""
Telegram Crypto Wallet Monitor Bot - Step 6: Remove Wallet Functionality
Added wallet removal with enhanced UX and error handling.
"""

import logging
import os
import signal
import sys
import time
from telegram import Update
from telegram.ext import Application

from bot.utils.config import Config
from bot.utils.handler_registry import HandlerRegistry
from bot.handlers import StartHandler, HelpHandler, ListHandler, AddHandler, CheckHandler, RemoveHandler

# Setup logging and configuration
logger = Config.setup_logging()

def cleanup_existing_processes():
    """Clean up any existing bot processes before starting."""
    try:
        import subprocess
        
        # Get current script name
        current_script = os.path.basename(__file__)
        current_pid = os.getpid()
        
        logger.info("Checking for existing bot processes...")
        
        # Find processes running this script (excluding current process)
        try:
            result = subprocess.run(
                ['pgrep', '-f', f'python.*{current_script}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                pids = [pid.strip() for pid in pids if pid.strip() and int(pid.strip()) != current_pid]
                
                if pids:
                    logger.info(f"Found {len(pids)} existing bot process(es), terminating...")
                    
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            logger.info(f"Terminated process {pid}")
                        except ProcessLookupError:
                            # Process already dead
                            pass
                        except Exception as e:
                            logger.warning(f"Could not terminate process {pid}: {e}")
                    
                    # Give processes time to clean up
                    time.sleep(2)
                    logger.info("Process cleanup completed")
                else:
                    logger.info("No existing bot processes found")
            else:
                logger.info("No existing bot processes found")
                
        except subprocess.TimeoutExpired:
            logger.warning("Process check timed out")
        except FileNotFoundError:
            # pgrep not available, try alternative method
            logger.info("pgrep not available, skipping process cleanup")
        except Exception as e:
            logger.warning(f"Error during process cleanup: {e}")
            
    except Exception as e:
        logger.error(f"Failed to cleanup existing processes: {e}")

def setup_signal_handlers():
    """Setup graceful shutdown signal handlers."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination

def setup_handlers() -> HandlerRegistry:
    """Setup and register all command handlers."""
    registry = HandlerRegistry()
    
    # Register handlers
    start_handler = StartHandler()
    help_handler = HelpHandler(handler_registry=registry)
    list_handler = ListHandler()
    add_handler = AddHandler()
    check_handler = CheckHandler()
    remove_handler = RemoveHandler()
    
    registry.register_handler(start_handler)
    registry.register_handler(help_handler)
    registry.register_handler(list_handler)
    registry.register_handler(add_handler)
    registry.register_handler(check_handler)
    registry.register_handler(remove_handler)
    
    return registry

def main() -> None:
    """Main function to run the bot."""
    try:
        print("🤖 Starting Telegram Crypto Wallet Monitor Bot...")
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers()
        
        # Clean up any existing processes
        cleanup_existing_processes()
        
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Setup handlers
        handler_registry = setup_handlers()
        logger.info("Command handlers setup completed")
        
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Register all handlers with the application
        handler_registry.register_with_application(application)
        
        # Log startup information
        logger.info("=== Bot Startup Complete ===")
        logger.info(f"Environment: {Config.ENVIRONMENT}")
        logger.info(f"Authorized users: {len(Config.get_authorized_users())}")
        logger.info(f"Registered commands: {', '.join(handler_registry.list_commands())}")
        logger.info(f"Process ID: {os.getpid()}")
        logger.info("Bot is now running... Press Ctrl+C to stop")
        logger.info("===========================")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
    finally:
        logger.info("Bot shutdown completed")

if __name__ == '__main__':
    main()