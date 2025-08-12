#!/usr/bin/env python3
"""
DUEL LORDS Bot Guardian - Ultra Reliable Bot Keeper
Ensures the Discord bot never stops running
"""

import os
import sys
import time
import subprocess
import signal
import logging
import threading
from datetime import datetime

# Setup robust logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [GUARDIAN] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('guardian.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

class BotGuardian:
    def __init__(self):
        self.running = True
        self.bot_process = None
        self.last_check = datetime.now()
        self.restart_count = 0
        self.health_checks = 0
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum} - Initiating graceful shutdown")
        self.running = False
        self._stop_bot()
        
    def _check_bot_status(self):
        """Check if Discord bot process is running"""
        try:
            # Check using pgrep
            result = subprocess.run(
                ['pgrep', '-f', 'discord_bot_runner.py'], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if result.stdout.strip():
                self.health_checks += 1
                if self.health_checks % 10 == 0:  # Log every 10th check
                    logger.info(f"✅ Bot healthy (check #{self.health_checks})")
                return True
            else:
                return False
                
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def _start_bot(self):
        """Start the Discord bot process"""
        try:
            logger.info("🚀 Starting DUEL LORDS Discord Bot...")
            
            # Kill any existing processes first
            subprocess.run(['pkill', '-f', 'discord_bot_runner'], 
                         capture_output=True, timeout=5)
            time.sleep(2)
            
            # Start fresh bot process
            self.bot_process = subprocess.Popen(
                [sys.executable, 'discord_bot_runner.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait and verify startup
            time.sleep(15)  # Give bot time to initialize
            
            if self._check_bot_status():
                self.restart_count += 1
                logger.info(f"✅ Bot started successfully (restart #{self.restart_count})")
                
                # Start output monitor in background
                monitor_thread = threading.Thread(
                    target=self._monitor_bot_output, 
                    daemon=True
                )
                monitor_thread.start()
                
                return True
            else:
                logger.error("❌ Bot failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False
    
    def _monitor_bot_output(self):
        """Monitor bot output for critical messages"""
        if not self.bot_process:
            return
            
        try:
            for line in iter(self.bot_process.stdout.readline, ''):
                if not line or not self.running:
                    break
                    
                line = line.strip()
                if line:
                    # Log important messages
                    if any(keyword in line.lower() for keyword in 
                          ['online', 'ready', 'connected', 'synced', 'error', 'failed']):
                        logger.info(f"BOT: {line}")
                        
        except Exception as e:
            logger.warning(f"Output monitoring stopped: {e}")
    
    def _stop_bot(self):
        """Stop bot process gracefully"""
        if self.bot_process:
            try:
                logger.info("🛑 Stopping bot process...")
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
                logger.info("✅ Bot stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Force killing bot process...")
                self.bot_process.kill()
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")
            finally:
                self.bot_process = None
    
    def _emergency_restart(self):
        """Emergency restart procedure"""
        logger.warning("🚨 EMERGENCY RESTART INITIATED")
        
        # Kill all related processes
        for cmd in ['discord_bot_runner', 'keep_bot_alive', 'start_discord_bot']:
            subprocess.run(['pkill', '-f', cmd], capture_output=True)
        
        time.sleep(5)
        return self._start_bot()
    
    def run(self):
        """Main guardian loop"""
        logger.info("💫 DUEL LORDS Bot Guardian v2.0 Started")
        logger.info("🛡️ Ultra-reliable bot protection enabled")
        logger.info("🔄 Monitoring every 15 seconds")
        
        # Initial start
        if not self._start_bot():
            logger.error("❌ Failed initial bot start")
            return
        
        check_interval = 15  # Check every 15 seconds
        failure_count = 0
        max_failures = 3
        
        while self.running:
            try:
                time.sleep(check_interval)
                
                if not self.running:
                    break
                
                # Health check
                if self._check_bot_status():
                    failure_count = 0  # Reset failure counter
                else:
                    failure_count += 1
                    logger.warning(f"⚠️ Bot not responding (failure {failure_count}/{max_failures})")
                    
                    if failure_count >= max_failures:
                        logger.error("💥 Bot has failed multiple health checks")
                        if self._emergency_restart():
                            failure_count = 0
                        else:
                            logger.critical("🔥 Emergency restart failed!")
                            time.sleep(30)  # Wait before trying again
                
                # Log status every 5 minutes
                if self.health_checks % 20 == 0:
                    uptime = datetime.now() - self.last_check
                    logger.info(f"📊 Guardian Status: {self.restart_count} restarts, {uptime} uptime")
                
            except KeyboardInterrupt:
                logger.info("🛑 Guardian shutdown requested")
                break
            except Exception as e:
                logger.error(f"❌ Guardian error: {e}")
                time.sleep(10)
        
        # Cleanup
        self._stop_bot()
        logger.info("🔒 Guardian stopped")

def main():
    """Main entry point"""
    # Verify Discord token
    if not os.getenv('DISCORD_TOKEN'):
        logger.error("❌ DISCORD_TOKEN environment variable not found!")
        sys.exit(1)
    
    # Verify bot file exists
    if not os.path.exists('discord_bot_runner.py'):
        logger.error("❌ discord_bot_runner.py not found!")
        sys.exit(1)
    
    logger.info(f"🌟 Working Directory: {os.getcwd()}")
    logger.info(f"🐍 Python: {sys.version}")
    
    guardian = BotGuardian()
    guardian.run()

if __name__ == "__main__":
    main()