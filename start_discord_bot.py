#!/usr/bin/env python3
"""
Persistent Discord Bot Runner for DUEL LORDS
This script ensures the bot stays running permanently
"""

import os
import sys
import time
import subprocess
import signal
import logging
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_persistent.log')
    ]
)
logger = logging.getLogger(__name__)

class PersistentBotRunner:
    def __init__(self):
        self.bot_process = None
        self.running = True
        self.restart_count = 0
        self.max_restarts = 10
        
    def start_bot(self):
        """Start the Discord bot process"""
        try:
            logger.info("Starting DUEL LORDS Discord Bot...")
            self.bot_process = subprocess.Popen(
                [sys.executable, 'discord_bot_runner.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start log monitor in separate thread
            log_thread = Thread(target=self.monitor_logs, daemon=True)
            log_thread.start()
            
            logger.info(f"Bot started with PID: {self.bot_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            return False
    
    def monitor_logs(self):
        """Monitor bot output logs"""
        if not self.bot_process:
            return
            
        try:
            for line in iter(self.bot_process.stdout.readline, ''):
                if line:
                    print(f"BOT: {line.strip()}")
                    
                    # Check for successful connection
                    if "DUEL LORDS is online!" in line:
                        logger.info("✅ Bot successfully connected to Discord")
                        self.restart_count = 0  # Reset restart counter on success
                        
                    # Check for critical errors
                    elif "Failed to connect" in line or "Connection lost" in line:
                        logger.warning("⚠️ Bot connection issue detected")
                        
        except Exception as e:
            logger.error(f"Log monitoring error: {e}")
    
    def is_bot_running(self):
        """Check if bot process is still running"""
        if self.bot_process is None:
            return False
            
        poll = self.bot_process.poll()
        return poll is None
    
    def stop_bot(self):
        """Stop the bot process gracefully"""
        if self.bot_process and self.is_bot_running():
            logger.info("Stopping bot process...")
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Bot didn't stop gracefully, forcing kill...")
                self.bot_process.kill()
            finally:
                self.bot_process = None
    
    def restart_bot(self):
        """Restart the bot process"""
        if self.restart_count >= self.max_restarts:
            logger.error(f"Max restart attempts ({self.max_restarts}) reached. Stopping.")
            self.running = False
            return False
            
        self.restart_count += 1
        logger.info(f"Restarting bot (attempt {self.restart_count}/{self.max_restarts})...")
        
        self.stop_bot()
        time.sleep(5)  # Wait before restart
        
        return self.start_bot()
    
    def run(self):
        """Main loop to keep bot running"""
        logger.info("🚀 Starting Persistent DUEL LORDS Bot Runner...")
        
        # Initial start
        if not self.start_bot():
            logger.error("Failed to start bot initially. Exiting.")
            return
        
        try:
            while self.running:
                time.sleep(30)  # Check every 30 seconds
                
                if not self.is_bot_running():
                    logger.warning("🔄 Bot process stopped unexpectedly. Restarting...")
                    if not self.restart_bot():
                        break
                else:
                    # Bot is running fine
                    if self.restart_count > 0:
                        logger.info(f"✅ Bot stable. Reset restart counter from {self.restart_count}")
                        self.restart_count = 0
                        
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error in main loop: {e}")
        finally:
            logger.info("🔒 Cleaning up...")
            self.running = False
            self.stop_bot()
            logger.info("✅ Bot runner stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}. Shutting down...")
    global runner
    if 'runner' in globals():
        runner.running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # Check for Discord token
    if not os.getenv('DISCORD_TOKEN'):
        logger.error("❌ DISCORD_TOKEN environment variable not found!")
        sys.exit(1)
    
    logger.info("💫 DUEL LORDS Persistent Bot Runner v1.0")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working Directory: {os.getcwd()}")
    
    runner = PersistentBotRunner()
    runner.run()