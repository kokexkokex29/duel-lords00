"""
DUEL LORDS - BombSquad Tournament Discord Bot
Enhanced bot with comprehensive tournament management and duel scheduling
"""

import os
import discord
from discord.ext import commands, tasks
import logging
import asyncio
from datetime import datetime, timedelta
from database import Database
from utils.scheduler import MatchScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DuelLordsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.dm_messages = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Initialize database
        self.db = Database()
        
        # Initialize scheduler 
        self.scheduler = None
        
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        try:
            # Initialize scheduler now that we have an event loop
            from utils.scheduler import MatchScheduler
            self.scheduler = MatchScheduler(self)
            
            # Load command cogs
            await self.load_extension('commands.admin_commands')
            await self.load_extension('commands.player_commands')
            await self.load_extension('commands.match_commands')
            await self.load_extension('commands.tournament_commands')
            await self.load_extension('commands.general_commands')
            await self.load_extension('missing_commands')
            
            print("✅ All cogs loaded successfully")
            
            # Start background tasks
            if not self.duel_reminder_task.is_running():
                self.duel_reminder_task.start()
            
            # Sync slash commands
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
            
        except Exception as e:
            print(f"❌ Error loading cogs: {e}")
            logger.error(f"Error loading cogs: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'🎮 DUEL LORDS is online!')
        if self.user:
            print(f'Bot: {self.user.name} (ID: {self.user.id})')
        print(f'Servers: {len(self.guilds)}')
        print('=' * 50)
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="BombSquad Tournaments | /help"
            ),
            status=discord.Status.online
        )
    
    async def on_application_command_error(self, interaction: discord.Interaction, error: Exception):
        """Handle slash command errors"""
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"❌ Error: {str(error)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Error: {str(error)}", ephemeral=True)
        except:
            pass
        
        print(f"❌ Command error: {error}")
        logger.error(f"Command error: {error}")
    
    @tasks.loop(minutes=1)
    async def duel_reminder_task(self):
        """Check for upcoming duels and send reminders"""
        try:
            matches = self.db.get_upcoming_matches()
            current_time = datetime.now()
            
            for match in matches:
                match_time = datetime.fromisoformat(match['scheduled_time'])
                time_diff = match_time - current_time
                
                # Send reminder 5 minutes before
                if timedelta(minutes=4, seconds=30) <= time_diff <= timedelta(minutes=5, seconds=30):
                    if not match.get('reminder_sent', False):
                        await self.send_duel_reminder(match)
                        # Update reminder status
                        self.db.update_match_reminder_status(match['id'], True)
                
                # Start the duel if time has come
                elif time_diff.total_seconds() <= 0 and match['status'] == 'scheduled':
                    await self.start_duel(match)
                    
        except Exception as e:
            logger.error(f"Error in duel reminder task: {e}")
    
    async def send_duel_reminder(self, match):
        """Send duel reminder to both players"""
        try:
            from utils.embeds import create_duel_reminder_embed
            
            player1_id = int(match['player1_id'])
            player2_id = int(match['player2_id'])
            
            player1 = await self.fetch_user(player1_id)
            player2 = await self.fetch_user(player2_id)
            
            embed = create_duel_reminder_embed(match)
            
            # Send DM to both players
            try:
                await player1.send(embed=embed)
                print(f"✅ Reminder sent to {player1.name}")
            except:
                print(f"❌ Failed to send reminder to {player1.name}")
            
            try:
                await player2.send(embed=embed)
                print(f"✅ Reminder sent to {player2.name}")
            except:
                print(f"❌ Failed to send reminder to {player2.name}")
            
            # Also send to channel if specified
            if match.get('channel_id'):
                try:
                    channel = self.get_channel(int(match['channel_id']))
                    if channel and hasattr(channel, 'send') and callable(getattr(channel, 'send', None)):
                        content = f"⚔️ Duel Reminder!\n<@{player1_id}> vs <@{player2_id}>"
                        await channel.send(content=content, embed=embed)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error sending duel reminder: {e}")
    
    async def start_duel(self, match):
        """Start the duel and notify players"""
        try:
            from utils.embeds import create_duel_start_embed
            
            # Update match status
            self.db.update_match_status(match['id'], 'active')
            
            player1_id = int(match['player1_id'])
            player2_id = int(match['player2_id'])
            
            embed = create_duel_start_embed(match)
            
            # Send to channel
            if match.get('channel_id'):
                try:
                    channel = self.get_channel(int(match['channel_id']))
                    if channel and hasattr(channel, 'send') and callable(getattr(channel, 'send', None)):
                        content = f"🚀 Duel Starting Now!\n<@{player1_id}> vs <@{player2_id}>"
                        await channel.send(content=content, embed=embed)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error starting duel: {e}")
    
    @duel_reminder_task.before_loop
    async def before_duel_reminder_task(self):
        """Wait until bot is ready before starting reminder task"""
        await self.wait_until_ready()

def run_bot():
    """Run the Discord bot"""
    import asyncio
    
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        bot = DuelLordsBot()
        token = os.environ.get("DISCORD_TOKEN")
        
        if not token:
            logger.error("DISCORD_TOKEN environment variable not set")
            return
        
        bot.run(token)
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")
