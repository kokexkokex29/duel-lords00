"""
BombSquad Tournament Discord Bot
Enhanced bot with comprehensive tournament management
"""

import os
import discord
from discord.ext import commands, tasks
import logging
import asyncio
from datetime import datetime, timedelta
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TournamentBot(commands.Bot):
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
        
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        try:
            # Load command cogs
            await self.load_extension('commands.admin_commands')
            await self.load_extension('commands.player_commands')
            await self.load_extension('commands.match_commands')
            await self.load_extension('commands.tournament_commands')
            await self.load_extension('commands.general_commands')
            
            print("✅ All cogs loaded successfully")
            
            # Start background tasks
            self.match_reminder_task.start()
            
            # Sync slash commands
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
            
        except Exception as e:
            print(f"❌ Error loading cogs: {e}")
            logger.error(f"Error loading cogs: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f'🎮 BombSquad Tournament Bot is online!')
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
    async def match_reminder_task(self):
        """Check for upcoming matches and send reminders"""
        try:
            matches = self.db.get_upcoming_matches()
            current_time = datetime.now()
            
            for match in matches:
                match_time = datetime.fromisoformat(match['scheduled_time'])
                time_diff = match_time - current_time
                
                # Send reminder 5 minutes before
                if timedelta(minutes=4, seconds=30) <= time_diff <= timedelta(minutes=5, seconds=30):
                    if not match.get('reminder_sent', False):
                        await self.send_match_reminder(match)
                        self.db.update_match_reminder_status(match['id'], True)
                
                # Start the match if time has come
                elif time_diff.total_seconds() <= 0 and match['status'] == 'scheduled':
                    await self.start_match(match)
                    
        except Exception as e:
            logger.error(f"Error in match reminder task: {e}")
    
    @match_reminder_task.before_loop
    async def before_match_reminder_task(self):
        """Wait until bot is ready before starting reminder task"""
        await self.wait_until_ready()
    
    async def send_match_reminder(self, match):
        """Send match reminder to both players"""
        try:
            player1_id = int(match['player1_id'])
            player2_id = int(match['player2_id'])
            
            embed = discord.Embed(
                title="🔔 Match Reminder",
                description=f"Your match is starting in 5 minutes!",
                color=discord.Color.orange()
            )
            
            embed.add_field(name="Match ID", value=match['id'], inline=True)
            embed.add_field(name="Server", value="18.228.228.44:3827", inline=True)
            embed.add_field(name="Time", value=match['scheduled_time'], inline=False)
            
            # Send DM to both players
            try:
                player1 = await self.fetch_user(player1_id)
                await player1.send(embed=embed)
                print(f"✅ Reminder sent to {player1.name}")
            except:
                pass
            
            try:
                player2 = await self.fetch_user(player2_id)
                await player2.send(embed=embed)
                print(f"✅ Reminder sent to {player2.name}")
            except:
                pass
                    
        except Exception as e:
            logger.error(f"Error sending match reminder: {e}")
    
    async def start_match(self, match):
        """Start the match and notify players"""
        try:
            # Update match status
            self.db.update_match_status(match['id'], 'active')
            
            player1_id = int(match['player1_id'])
            player2_id = int(match['player2_id'])
            
            embed = discord.Embed(
                title="🚀 Match Starting Now!",
                description=f"Join the BombSquad server to compete!",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Match ID", value=match['id'], inline=True)
            embed.add_field(name="Server", value="18.228.228.44:3827", inline=True)
            embed.add_field(name="Players", value=f"<@{player1_id}> vs <@{player2_id}>", inline=False)
            
            # Send to channel if available
            if match.get('channel_id'):
                try:
                    channel = self.get_channel(int(match['channel_id']))
                    if channel:
                        await channel.send(embed=embed)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error starting match: {e}")

def run_bot():
    """Run the Discord bot"""
    try:
        bot = TournamentBot()
        token = os.environ.get("DISCORD_TOKEN")
        
        if not token:
            logger.error("DISCORD_TOKEN environment variable not set")
            return
        
        bot.run(token)
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    run_bot()