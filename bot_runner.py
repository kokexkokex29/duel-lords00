#!/usr/bin/env python3
"""
Clan Lords |Bombsquad Bot Runner - Main bot execution with Guardian
This runs the bot with auto-restart capabilities
"""

import os
import sys
import time
import subprocess
import logging
import signal
import threading
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [BOT-RUNNER] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_runner.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class BotRunner:
    def __init__(self, register_signals=True):
        self.running = True
        self.bot_process = None
        self.restart_count = 0
        
        # Only register signal handlers if in main thread
        if register_signals:
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            except ValueError:
                # Running in thread, skip signal handling
                pass
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum} - Shutting down gracefully")
        self.running = False
        self._stop_bot()
        sys.exit(0)
        
    def _check_bot_status(self):
        """Check if bot process is still running"""
        if self.bot_process:
            return self.bot_process.poll() is None
        return False
    
    def _start_bot(self):
        """Start the Discord bot process"""
        try:
            logger.info("🚀 Starting Clan Lords |Bombsquad Discord Bot...")
            
            # Kill any existing bot processes
            try:
                subprocess.run(['pkill', '-f', 'bot.py'], capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
            
            # Start bot process
            self.bot_process = subprocess.Popen(
                [sys.executable, 'full_bot.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.restart_count += 1
            logger.info(f"✅ Bot started (restart #{self.restart_count})")
            
            # Monitor output in separate thread
            output_thread = threading.Thread(
                target=self._monitor_output,
                daemon=True
            )
            output_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False
    
    def _monitor_output(self):
        """Monitor bot output and log important messages"""
        if not self.bot_process:
            return
            
        try:
            while self.running and self.bot_process:
                line = self.bot_process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    # Log important bot messages
                    if any(keyword in line.lower() for keyword in [
                        'online', 'ready', 'connected', 'synced', 'error', 
                        'failed', 'crash', 'exception'
                    ]):
                        logger.info(f"BOT: {line}")
                        
        except Exception as e:
            logger.error(f"Error monitoring bot output: {e}")
    
    def _stop_bot(self):
        """Stop the bot process"""
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
                logger.info("✅ Bot stopped gracefully")
            except subprocess.TimeoutExpired:
                self.bot_process.kill()
                logger.warning("⚠️ Bot force killed")
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")
            
            self.bot_process = None
    
    def run_forever(self):
        """Main loop - keep bot running forever"""
        logger.info("🎮 Clan Lords |Bombsquad Bot Runner starting...")
        
        # Check for Discord token
        if not os.getenv('DISCORD_TOKEN'):
            logger.error("❌ DISCORD_TOKEN not found in environment!")
            logger.error("Please add your Discord bot token to Replit Secrets")
            return
        
        logger.info("✅ Discord token found")
        
        # Main supervision loop
        while self.running:
            try:
                # Start bot if not running
                if not self._check_bot_status():
                    logger.info("Bot not running, starting...")
                    if not self._start_bot():
                        logger.error("Failed to start bot, retrying in 30 seconds...")
                        time.sleep(30)
                        continue
                
                # Health check every 30 seconds
                time.sleep(30)
                
                # Check if bot is still healthy
                if not self._check_bot_status():
                    logger.warning("⚠️ Bot process died, restarting...")
                    self._stop_bot()
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                logger.info("👋 Shutdown requested by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(10)
        
        # Cleanup
        self._stop_bot()
        logger.info("🛑 Bot Runner stopped")

def main():
    """Main entry point"""
    runner = BotRunner()
    runner.run_forever()

if __name__ == "__main__":
    main()