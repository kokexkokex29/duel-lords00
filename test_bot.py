#!/usr/bin/env python3
"""
Test script to verify Discord bot can connect and work properly
Run this to test the bot independently from the web server
"""

import os
import logging
import asyncio
from bot import BombSquadBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot():
    """Test the Discord bot connection"""
    bot = BombSquadBot()
    token = os.environ.get("DISCORD_TOKEN")
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return False
    
    try:
        logger.info("Testing Discord bot connection...")
        await bot.login(token)
        logger.info("✅ Bot login successful!")
        
        logger.info("Testing command loading...")
        # The setup_hook should load all commands
        await bot.setup_hook()
        logger.info("✅ Commands loaded successfully!")
        
        logger.info("✅ Bot test completed successfully!")
        await bot.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Bot test failed: {e}")
        await bot.close()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot())
    if success:
        print("\n🎉 Discord bot is ready to run!")
        print("To start the bot, run: python -c \"from bot import run_bot; run_bot()\"")
    else:
        print("\n❌ Bot test failed. Check the logs above for details.")