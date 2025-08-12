"""
Match Commands for DUEL LORDS Discord Bot
Enhanced duel system with private messaging and automatic reminders
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import re
import uuid

class MatchCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="duel", description="Challenge players to a duel - /duel @player1 @player2 hour minute")
    @app_commands.describe(
        player1="First player",
        player2="Second player", 
        hour="Hour (0-23)",
        minute="Minute (0-59)"
    )
    async def create_duel(
        self, 
        interaction: discord.Interaction,
        player1: discord.Member,
        player2: discord.Member,
        hour: int,
        minute: int
    ):
        """Create a new duel between two players"""
        
        # Validate hour and minute
        if not (0 <= hour <= 23):
            await interaction.response.send_message(
                "❌ Hour must be between 0 and 23", 
                ephemeral=True
            )
            return
            
        if not (0 <= minute <= 59):
            await interaction.response.send_message(
                "❌ Minute must be between 0 and 59", 
                ephemeral=True
            )
            return

        # Check if both players are registered
        player1_data = self.db.get_player(str(player1.id))
        player2_data = self.db.get_player(str(player2.id))

        if not player1_data:
            await interaction.response.send_message(
                f"❌ {player1.display_name} is not registered for the tournament. They must use `/register` first",
                ephemeral=True
            )
            return

        if not player2_data:
            await interaction.response.send_message(
                f"❌ {player2.display_name} is not registered for the tournament. They must use `/register` first",
                ephemeral=True
            )
            return

        # Check if trying to duel the same person
        if player1.id == player2.id:
            await interaction.response.send_message(
                "❌ A player cannot duel themselves!",
                ephemeral=True
            )
            return

        # Create scheduled time for today at specified hour:minute
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time has passed today, schedule for tomorrow
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)

        # Create match in database
        match_id = str(uuid.uuid4())[:8]
        match_data = {
            'id': match_id,
            'player1_id': str(player1.id),
            'player2_id': str(player2.id),
            'scheduled_time': scheduled_time.isoformat(),
            'status': 'scheduled',
            'channel_id': str(interaction.channel.id) if interaction.channel else None,
            'created_by': str(interaction.user.id),
            'created_at': datetime.now().isoformat(),
            'reminder_sent': False
        }

        # Save to database
        self.db.create_match(
            challenger_id=str(player1.id),
            opponent_id=str(player2.id),
            scheduled_time=scheduled_time.isoformat(),
            description=f"Duel between {player1.display_name} and {player2.display_name}"
        )

        # Create main embed for channel
        embed = discord.Embed(
            title="⚔️ New Duel Scheduled!",
            description="A new duel has been created successfully",
            color=0xFFD700,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="🥊 Fighters",
            value=f"{player1.mention} **VS** {player2.mention}",
            inline=False
        )

        embed.add_field(
            name="🕐 Duel Time",
            value=f"<t:{int(scheduled_time.timestamp())}:F>\n<t:{int(scheduled_time.timestamp())}:R>",
            inline=False
        )

        embed.add_field(
            name="🆔 Match ID",
            value=f"`{match_id}`",
            inline=True
        )

        embed.add_field(
            name="🎯 Server Info",
            value="IP: `18.228.228.44:3827`",
            inline=True
        )

        embed.add_field(
            name="💡 Next Steps",
            value="• Both players will receive DM notifications\n• 5-minute reminder before match\n• Use `/record_result` after the match",
            inline=False
        )

        embed.set_footer(text="DUEL LORDS • Good luck fighters!")
        
        await interaction.response.send_message(embed=embed)

        # Send private messages to both players
        try:
            dm_embed = discord.Embed(
                title="⚔️ Duel Challenge!",
                description=f"You have been challenged to a duel!",
                color=0xFF6B6B,
                timestamp=datetime.now()
            )
            
            dm_embed.add_field(
                name="🥊 Opponent",
                value=f"**{player2.display_name if player1.id == player1.id else player1.display_name}**",
                inline=True
            )
            
            dm_embed.add_field(
                name="🕐 Match Time",
                value=f"<t:{int(scheduled_time.timestamp())}:F>",
                inline=True
            )
            
            dm_embed.add_field(
                name="🌐 Server",
                value="18.228.228.44:3827",
                inline=False
            )
            
            dm_embed.add_field(
                name="🆔 Match ID",
                value=f"`{match_id}`",
                inline=True
            )
            
            dm_embed.set_footer(text="DUEL LORDS • Prepare for battle!")
            
            # Send to both players
            await player1.send(embed=dm_embed)
            await player2.send(embed=dm_embed)
            
        except discord.Forbidden:
            # If DMs fail, mention it in the channel
            await interaction.followup.send(
                "⚠️ Could not send DM notifications to one or both players. Please ensure DMs are enabled.",
                ephemeral=True
            )

    @app_commands.command(name="record_result", description="Record the result of a match")
    @app_commands.describe(
        match_id="Match ID to record result for",
        winner="Winner of the match",
        loser="Loser of the match",
        winner_kills="Winner's kill count",
        loser_kills="Loser's kill count"
    )
    async def record_result(
        self, 
        interaction: discord.Interaction,
        match_id: str,
        winner: discord.Member,
        loser: discord.Member,
        winner_kills: int = 0,
        loser_kills: int = 0
    ):
        """Record match result and update player statistics"""
        
        # Get match data
        match = self.db.get_match(match_id)
        if not match:
            await interaction.response.send_message(
                f"❌ Match with ID `{match_id}` not found",
                ephemeral=True
            )
            return
        
        # Verify participants
        participants = [match['player1_id'], match['player2_id']]
        if str(winner.id) not in participants or str(loser.id) not in participants:
            await interaction.response.send_message(
                "❌ Both winner and loser must be participants in this match",
                ephemeral=True
            )
            return
        
        # Update match status
        match['status'] = 'completed'
        match['winner_id'] = str(winner.id)
        match['completed_at'] = datetime.now().isoformat()
        match['winner_kills'] = winner_kills
        match['loser_kills'] = loser_kills
        
        self.db.update_match(match_id, match)
        
        # Update player statistics
        self.db.update_player_stats(str(winner.id), wins=1, kills=winner_kills)
        self.db.update_player_stats(str(loser.id), losses=1, kills=loser_kills)
        
        # Create result embed
        embed = discord.Embed(
            title="📊 Match Result Recorded",
            description=f"Results for match `{match_id}` have been saved",
            color=0x00FF00,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🏆 Winner", 
            value=f"{winner.mention}\n⚔️ {winner_kills} kills", 
            inline=True
        )
        
        embed.add_field(
            name="💀 Loser", 
            value=f"{loser.mention}\n⚔️ {loser_kills} kills", 
            inline=True
        )
        
        embed.add_field(
            name="📈 Stats Updated",
            value="Player statistics have been updated automatically",
            inline=False
        )
        
        embed.set_footer(text="DUEL LORDS • Good game!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="matches", description="Show scheduled matches")
    async def show_matches(self, interaction: discord.Interaction):
        """Show all scheduled matches"""
        matches = self.db.get_all_matches()
        
        if not matches:
            embed = discord.Embed(
                title="📅 No Matches Scheduled",
                description="No matches are currently scheduled",
                color=0xFAA61A
            )
            embed.add_field(
                name="💡 How to Schedule",
                value="Use `/duel @player1 @player2 hour minute` to create a match",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Filter active matches
        active_matches = [m for m in matches.values() if m['status'] in ['scheduled', 'accepted']]
        
        embed = discord.Embed(
            title="📅 Scheduled Matches",
            description=f"Total: {len(active_matches)} active matches",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        for match in active_matches[:10]:  # Show first 10
            try:
                player1 = await interaction.client.fetch_user(int(match['player1_id']))
                player2 = await interaction.client.fetch_user(int(match['player2_id']))
                
                scheduled_time = datetime.fromisoformat(match['scheduled_time'])
                time_str = f"<t:{int(scheduled_time.timestamp())}:R>"
                
                embed.add_field(
                    name=f"Match {match['id']}",
                    value=f"{player1.display_name} vs {player2.display_name}\n🕐 {time_str}",
                    inline=True
                )
            except:
                continue
        
        if len(active_matches) > 10:
            embed.add_field(
                name="📊 More Matches",
                value=f"And {len(active_matches) - 10} more matches...",
                inline=False
            )
        
        embed.set_footer(text="DUEL LORDS • Use /record_result to submit results")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cancel_match", description="Cancel a scheduled match")
    @app_commands.describe(match_id="Match ID to cancel")
    async def cancel_match(self, interaction: discord.Interaction, match_id: str):
        """Cancel a scheduled match"""
        match = self.db.get_match(match_id)
        
        if not match:
            await interaction.response.send_message(
                f"❌ Match with ID `{match_id}` not found",
                ephemeral=True
            )
            return
        
        # Check if user is participant or admin
        user_id = str(interaction.user.id)
        is_participant = user_id in [match['player1_id'], match['player2_id']]
        is_admin = (isinstance(interaction.user, discord.Member) and 
                   interaction.user.guild_permissions.administrator)
        
        if not (is_participant or is_admin):
            await interaction.response.send_message(
                "❌ Only match participants or administrators can cancel matches",
                ephemeral=True
            )
            return
        
        if match['status'] == 'completed':
            await interaction.response.send_message(
                "❌ Cannot cancel a completed match",
                ephemeral=True
            )
            return
        
        # Cancel the match
        match['status'] = 'cancelled'
        match['cancelled_at'] = datetime.now().isoformat()
        match['cancelled_by'] = user_id
        
        self.db.update_match(match_id, match)
        
        embed = discord.Embed(
            title="❌ Match Cancelled",
            description=f"Match `{match_id}` has been cancelled",
            color=0xFF6B6B,
            timestamp=datetime.now()
        )
        
        try:
            player1 = await interaction.client.fetch_user(int(match['player1_id']))
            player2 = await interaction.client.fetch_user(int(match['player2_id']))
            
            embed.add_field(
                name="🥊 Match",
                value=f"{player1.display_name} vs {player2.display_name}",
                inline=False
            )
        except:
            pass
        
        embed.add_field(
            name="🗑️ Cancelled by",
            value=interaction.user.display_name,
            inline=True
        )
        
        embed.set_footer(text="DUEL LORDS • Match cancelled")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MatchCommands(bot))