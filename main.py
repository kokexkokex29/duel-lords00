#!/usr/bin/env python3
"""
Clan Lords |Bombsquad - Main Application Entry Point
Runs Flask web dashboard and Discord bot management system
"""

import os
import threading
import time
import logging
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MAIN] %(message)s'
)
logger = logging.getLogger(__name__)

def run_discord_bot():
    """Run Discord bot if token is available"""
    try:
        if os.getenv('DISCORD_TOKEN'):
            logger.info("🎮 Starting Discord bot...")
            # Import only when needed and if token exists
            from bot_new import run_bot
            run_bot()
        else:
            logger.info("⚠️ Discord bot not started - token not found")
    except ImportError:
        logger.warning("⚠️ Discord bot dependencies not available")
    except Exception as e:
        logger.error(f"Error starting Discord bot: {e}")

# Start Discord bot in background thread when module is imported
def start_background_bot():
    """Start bot in background thread"""
    if os.getenv('DISCORD_TOKEN'):
        logger.info("🚀 Clan Lords |Bombsquad Tournament System Starting...")
        logger.info("✅ Discord token found")
        
        # Start Discord bot in background thread
        bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
        bot_thread.start()
        logger.info("✅ Discord bot started in background")
    else:
        logger.warning("⚠️ DISCORD_TOKEN not found - Bot not started")
        logger.info("Please add your Discord bot token to Replit Secrets")

# Auto-start bot when imported
start_background_bot()

def main():
    """Main function for direct execution"""
    logger.info("🚀 Clan Lords |Bombsquad Tournament System Starting...")
    
    # Check for Discord token
    if not os.getenv('DISCORD_TOKEN'):
        logger.error("❌ DISCORD_TOKEN not found!")
        logger.error("Please add your Discord bot token to Replit Secrets")
        return
    
    # Start Discord bot
    try:
        run_discord_bot()
    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
