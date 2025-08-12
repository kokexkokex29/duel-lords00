#!/usr/bin/env python3
"""
Discord Bot Runner for DUEL LORDS Tournament Bot
This script runs the Discord bot in a separate thread alongside the Flask web dashboard
"""

import os
import threading
import time
import logging
import asyncio
from bot import main as run_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_discord_bot():
    """Start the Discord bot in a separate thread"""
    logger.info("Starting Discord bot thread...")
    try:
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"Discord bot error: {e}")

def main():
    """Main function to start both Flask app and Discord bot"""
    # Check if Discord token is available
    discord_token = os.environ.get("DISCORD_TOKEN")
    if not discord_token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        logger.info("Please add your Discord bot token to Replit Secrets as DISCORD_TOKEN")
        return
    
    logger.info("DUEL LORDS Tournament System Starting...")
    logger.info("✅ Discord token found")
    
    # Start Discord bot in a separate thread
    bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
    bot_thread.start()
    logger.info("Discord bot thread started")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(10)
            if not bot_thread.is_alive():
                logger.warning("Discord bot thread died, restarting...")
                bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
                bot_thread.start()
    except KeyboardInterrupt:
        logger.info("Shutting down DUEL LORDS Tournament System...")

if __name__ == "__main__":
    main()