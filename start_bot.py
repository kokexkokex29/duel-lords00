#!/usr/bin/env python3
"""
Start the Discord bot independently from the web server
This script runs the bot with all commands available
"""

import os
import logging
import asyncio
from bot import BombSquadBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the Discord bot"""
    token = os.environ.get("DISCORD_TOKEN")
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    try:
        # Create bot instance
        bot = BombSquadBot()
        
        logger.info("🤖 Starting Discord Bot 'Duels Lords'...")
        logger.info("📋 All tournament commands will be available!")
        
        # Run the bot
        bot.run(token, log_handler=None)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    main()