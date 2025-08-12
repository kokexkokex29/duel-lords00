#!/usr/bin/env python3
"""
Keep DUEL LORDS Discord Bot Running Forever
Simple script to maintain bot uptime
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - KEEPER - %(message)s'
)
logger = logging.getLogger(__name__)

class BotKeeper:
    def __init__(self):
        self.running = True
        self.bot_process = None
        
    def check_bot_running(self):
        """Check if discord bot is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'discord_bot_runner'], 
                                 capture_output=True, text=True)
            return bool(result.stdout.strip())
        except:
            return False
    
    def start_bot(self):
        """Start the discord bot"""
        try:
            logger.info("🚀 Starting Discord Bot...")
            self.bot_process = subprocess.Popen(
                [sys.executable, 'discord_bot_runner.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(10)  # Give it time to start
            
            if self.check_bot_running():
                logger.info("✅ Bot started successfully")
                return True
            else:
                logger.error("❌ Bot failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            return False
    
    def stop_handler(self, signum, frame):
        """Handle stop signals"""
        logger.info("🛑 Received stop signal")
        self.running = False
        if self.bot_process:
            self.bot_process.terminate()
    
    def run(self):
        """Main keeper loop"""
        signal.signal(signal.SIGINT, self.stop_handler)
        signal.signal(signal.SIGTERM, self.stop_handler)
        
        logger.info("💫 DUEL LORDS Bot Keeper Started")
        logger.info("🔄 Will restart bot automatically if it stops")
        
        while self.running:
            try:
                if not self.check_bot_running():
                    logger.warning("⚠️ Bot not running, restarting...")
                    if self.start_bot():
                        logger.info("✅ Bot restarted successfully")
                    else:
                        logger.error("❌ Failed to restart bot, will try again in 30 seconds")
                else:
                    logger.info("💚 Bot is running healthy")
                
                # Check every 30 seconds
                for _ in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Error in keeper loop: {e}")
                time.sleep(10)
        
        logger.info("🔒 Bot Keeper stopped")

if __name__ == "__main__":
    if not os.getenv('DISCORD_TOKEN'):
        logger.error("❌ DISCORD_TOKEN not found!")
        sys.exit(1)
    
    keeper = BotKeeper()
    keeper.run()