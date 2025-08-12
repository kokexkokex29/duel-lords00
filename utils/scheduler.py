from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import discord
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MatchScheduler:
    def __init__(self, bot=None):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        logger.info("Match scheduler started")
    
    def set_bot(self, bot):
        """Set the bot instance after initialization"""
        self.bot = bot
    
    def schedule_match_reminder(self, match_id, reminder_time, guild_id):
        """Schedule a match reminder"""
        try:
            self.scheduler.add_job(
                self._send_match_reminder,
                DateTrigger(run_date=reminder_time),
                args=[match_id, guild_id],
                id=f"reminder_{match_id}",
                replace_existing=True
            )
            logger.info(f"Scheduled reminder for match {match_id} at {reminder_time}")
        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}")
    
    async def _send_match_reminder(self, match_id, guild_id):
        """Send match reminder"""
        try:
            # This would be implemented with the bot instance
            # For now, just log the reminder
            logger.info(f"Match reminder for {match_id} in guild {guild_id}")
        except Exception as e:
            logger.error(f"Error sending match reminder: {e}")
    
    def cancel_match_reminder(self, match_id):
        """Cancel a match reminder"""
        try:
            self.scheduler.remove_job(f"reminder_{match_id}")
            logger.info(f"Cancelled reminder for match {match_id}")
        except Exception as e:
            logger.error(f"Error cancelling reminder: {e}")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Match scheduler shutdown")
