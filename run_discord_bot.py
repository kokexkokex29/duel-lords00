#!/usr/bin/env python3
"""
Simple Discord bot runner
This will start the bot with all commands available
"""

import os
import sys
import logging
import asyncio
from bot import BombSquadBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the Discord bot"""
    
    # Check for Discord token
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN environment variable not found!")
        logger.error("Please make sure the Discord token is set in Replit Secrets")
        return
    
    logger.info("🤖 Starting Discord Bot: Duels Lords")
    logger.info("📋 Bot will load all tournament management commands")
    
    try:
        # Create bot instance
        bot = BombSquadBot()
        
        # Display available commands info
        logger.info("🎮 Available Commands:")
        logger.info("   📝 Player Commands: /register, /stats, /leaderboard")
        logger.info("   🏆 Tournament Commands: /create_tournament, /join_tournament")
        logger.info("   ⚔️ Match Commands: /challenge, /accept_match, /report_result")
        logger.info("   👑 Admin Commands: /admin_match, /admin_reset")
        logger.info("   ❓ General Commands: /help, /server, /ip")
        
        # Run the bot
        logger.info("🚀 Connecting to Discord...")
        bot.run(token)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error running bot: {e}")
        logger.error("Check the error details above for troubleshooting")

if __name__ == "__main__":
    main()