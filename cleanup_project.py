#!/usr/bin/env python3
"""
Project Cleanup Script
Removes development/testing files and organizes project for production
"""

import os
import shutil
import json
from pathlib import Path

class ProjectCleanup:
    """Clean up project files and organize for production."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.removed_files = []
        self.kept_files = []
        
    def cleanup_debug_files(self):
        """Remove debug and development files."""
        print("🧹 Cleaning up debug files...")
        
        debug_files = [
            "debug_auth_config.py",
            "debug_check_parsing.py",
            "disable_bot_autocomplete.py",
            "set_minimal_commands.py"
        ]
        
        for file_name in debug_files:
            if os.path.exists(file_name):
                os.remove(file_name)
                self.removed_files.append(file_name)
                print(f"   ✅ Removed: {file_name}")
        
        if not any(os.path.exists(f) for f in debug_files):
            print("   ✅ No debug files found")
    
    def cleanup_chat_id_scripts(self):
        """Remove chat ID finding scripts."""
        print("🧹 Cleaning up chat ID scripts...")
        
        chat_scripts = [
            "find_chat_id.py",
            "get_group_chat_id.py", 
            "get_team_user_ids.py",
            "quick_get_chat_id.py",
            "simple_chat_finder.py"
        ]
        
        for file_name in chat_scripts:
            if os.path.exists(file_name):
                os.remove(file_name)
                self.removed_files.append(file_name)
                print(f"   ✅ Removed: {file_name}")
        
        if not any(os.path.exists(f) for f in chat_scripts):
            print("   ✅ No chat ID scripts found")
    
    def cleanup_test_files(self):
        """Remove test files."""
        print("🧹 Cleaning up test files...")
        
        test_files = [
            "test_daily_reports_30s.py",
            "test_group_daily_report.py", 
            "cleanup_test_data.py"
        ]
        
        for file_name in test_files:
            if os.path.exists(file_name):
                os.remove(file_name)
                self.removed_files.append(file_name)
                print(f"   ✅ Removed: {file_name}")
        
        if not any(os.path.exists(f) for f in test_files):
            print("   ✅ No test files found")
    
    def cleanup_shell_scripts(self):
        """Remove temporary shell scripts."""
        print("🧹 Cleaning up shell scripts...")
        
        shell_scripts = [
            "test_reports_30s.sh"
        ]
        
        for file_name in shell_scripts:
            if os.path.exists(file_name):
                os.remove(file_name)
                self.removed_files.append(file_name)
                print(f"   ✅ Removed: {file_name}")
        
        if not any(os.path.exists(f) for f in shell_scripts):
            print("   ✅ No temporary shell scripts found")
    
    def cleanup_log_files(self, keep_main_logs=True):
        """Clean up unnecessary log files."""
        print("🧹 Cleaning up log files...")
        
        if keep_main_logs:
            print("   ✅ Keeping main logs (telegram_bot.log, daily_reports.log)")
            return
        
        log_files = [
            "test_reports.log",
            "debug.log",
            "temp.log"
        ]
        
        for file_name in log_files:
            if os.path.exists(file_name):
                os.remove(file_name)
                self.removed_files.append(file_name)
                print(f"   ✅ Removed: {file_name}")
        
        if not any(os.path.exists(f) for f in log_files):
            print("   ✅ No temporary log files found")
    
    def cleanup_python_cache(self):
        """Remove Python cache files."""
        print("🧹 Cleaning up Python cache...")
        
        cache_dirs = []
        cache_files = []
        
        # Find __pycache__ directories
        for root, dirs, files in os.walk(self.project_root):
            for dir_name in dirs[:]:  # Use slice to avoid modification during iteration
                if dir_name == "__pycache__":
                    cache_path = Path(root) / dir_name
                    cache_dirs.append(str(cache_path))
                    dirs.remove(dir_name)  # Don't recurse into __pycache__
        
        # Find .pyc files
        for root, dirs, files in os.walk(self.project_root):
            for file_name in files:
                if file_name.endswith(('.pyc', '.pyo')):
                    cache_path = Path(root) / file_name
                    cache_files.append(str(cache_path))
        
        # Remove cache directories
        for cache_dir in cache_dirs:
            shutil.rmtree(cache_dir, ignore_errors=True)
            print(f"   ✅ Removed cache: {cache_dir}")
        
        # Remove cache files
        for cache_file in cache_files:
            try:
                os.remove(cache_file)
                print(f"   ✅ Removed cache: {cache_file}")
            except OSError:
                pass
        
        if not cache_dirs and not cache_files:
            print("   ✅ No Python cache found")
    
    def validate_core_files(self):
        """Validate that core production files exist."""
        print("🔍 Validating core files...")
        
        required_files = {
            "telegram_bot.py": "Main bot script",
            "main.py": "Daily report scheduler", 
            "wallets.json": "Wallet configuration",
            "requirements.txt": "Python dependencies",
            ".env": "Environment configuration",
            "README.md": "Documentation",
            "UAT_Testing_Guide.md": "Testing guide",
            "start_daily_reports.sh": "Daily reports startup script"
        }
        
        missing_files = []
        for file_name, description in required_files.items():
            if os.path.exists(file_name):
                self.kept_files.append(f"{file_name} - {description}")
                print(f"   ✅ {file_name} - {description}")
            else:
                missing_files.append(f"{file_name} - {description}")
                print(f"   ❌ {file_name} - {description}")
        
        if missing_files:
            print(f"\n⚠️  Missing {len(missing_files)} required files:")
            for file in missing_files:
                print(f"     - {file}")
    
    def validate_bot_structure(self):
        """Validate bot directory structure."""
        print("🔍 Validating bot structure...")
        
        required_dirs = {
            "bot/": "Bot package",
            "bot/handlers/": "Command handlers",
            "bot/services/": "Business logic services", 
            "bot/utils/": "Utilities and config"
        }
        
        for dir_path, description in required_dirs.items():
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                print(f"   ✅ {dir_path} - {description}")
            else:
                print(f"   ❌ {dir_path} - {description}")
    
    def show_final_structure(self):
        """Show the final clean project structure."""
        print("\n📁 Final Project Structure:")
        print("=" * 50)
        
        def print_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
                
            items = []
            try:
                items = sorted(os.listdir(path))
            except PermissionError:
                return
            
            # Filter out hidden files and cache
            items = [item for item in items if not item.startswith('.') and item != '__pycache__']
            
            for i, item in enumerate(items):
                item_path = os.path.join(path, item)
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                
                if os.path.isdir(item_path):
                    print(f"{prefix}{current_prefix}{item}/")
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    print_tree(item_path, next_prefix, max_depth, current_depth + 1)
                else:
                    print(f"{prefix}{current_prefix}{item}")
        
        print("telegram-crypto-bot/")
        print_tree(".", max_depth=3)
    
    def create_gitignore(self):
        """Create/update .gitignore file."""
        print("📝 Creating/updating .gitignore...")
        
        gitignore_content = """# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
!daily_reports.log
!telegram_bot.log

# Temporary files
*.tmp
*.temp
temp/

# Test files
test_*.py
debug_*.py
*_test.py

# Data files (optional - remove these lines if you want to track them)
wallet_balances.csv
wallets.json.backup

# Documentation drafts
*.md.backup
*.md.tmp
"""
        
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        
        print("   ✅ .gitignore created/updated")

def main():
    """Main cleanup function."""
    print("🧹 ======= PROJECT CLEANUP =======")
    print("🎯 Organizing project for production")
    print("⚠️  This will remove development files")
    print("==================================")
    
    # Confirm cleanup
    confirm = input("\n❓ Proceed with project cleanup? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Cleanup cancelled")
        return
    
    print("\n🚀 Starting project cleanup...")
    
    # Initialize cleanup
    cleanup = ProjectCleanup()
    
    # Perform cleanup operations
    cleanup.cleanup_debug_files()
    cleanup.cleanup_chat_id_scripts()
    cleanup.cleanup_test_files()
    cleanup.cleanup_shell_scripts()
    cleanup.cleanup_log_files(keep_main_logs=True)
    cleanup.cleanup_python_cache()
    
    print("\n" + "="*50)
    
    # Validate project structure
    cleanup.validate_core_files()
    cleanup.validate_bot_structure()
    
    # Create/update project files
    cleanup.create_gitignore()
    
    # Show results
    print(f"\n✅ Cleanup completed successfully!")
    print(f"   • Files removed: {len(cleanup.removed_files)}")
    print(f"   • Core files validated: {len(cleanup.kept_files)}")
    
    if cleanup.removed_files:
        print(f"\n📋 Removed files:")
        for file in cleanup.removed_files[:10]:  # Show first 10
            print(f"   - {file}")
        if len(cleanup.removed_files) > 10:
            print(f"   ... and {len(cleanup.removed_files) - 10} more")
    
    # Show final structure
    cleanup.show_final_structure()
    
    print("\n🎉 Your project is now clean and production-ready!")
    print("📋 Next steps:")
    print("   1. Verify .env configuration")
    print("   2. Test bot: python telegram_bot.py")
    print("   3. Test daily reports: python main.py test")
    print("   4. Start production: ./start_daily_reports.sh")
    print("   5. Commit to version control")

if __name__ == "__main__":
    main()