"""
Additional Commands for DUEL LORDS Discord Bot
Commands that were missing from the original implementation
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class MissingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="challenge", description="Challenge another player to a duel")
    @app_commands.describe(player="Player to challenge")
    async def challenge(self, interaction: discord.Interaction, player: discord.Member):
        """Challenge another player"""
        challenger = interaction.user
        
        if challenger.id == player.id:
            await interaction.response.send_message("❌ You cannot challenge yourself!", ephemeral=True)
            return
            
        # Check if both players are registered
        challenger_data = self.db.get_player(str(challenger.id))
        player_data = self.db.get_player(str(player.id))
        
        if not challenger_data:
            await interaction.response.send_message("❌ You must register first using `/register`", ephemeral=True)
            return
            
        if not player_data:
            await interaction.response.send_message(f"❌ {player.mention} is not registered for the tournament", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚔️ Challenge Issued!",
            description=f"{challenger.mention} has challenged {player.mention} to a duel!",
            color=0xFF6B6B,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🥊 Challenger",
            value=challenger.mention,
            inline=True
        )
        
        embed.add_field(
            name="🎯 Opponent",
            value=player.mention,
            inline=True
        )
        
        embed.add_field(
            name="📋 Next Steps",
            value="Use `/duel` command to schedule the match with specific time",
            inline=False
        )
        
        embed.set_footer(text="DUEL LORDS • Ready to fight!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="accept_match", description="Accept a match challenge")
    @app_commands.describe(match_id="Match ID to accept")
    async def accept_match(self, interaction: discord.Interaction, match_id: str):
        """Accept a match challenge"""
        match = self.db.get_match(match_id)
        
        if not match:
            await interaction.response.send_message(f"❌ No match found with ID `{match_id}`", ephemeral=True)
            return
            
        user_id = str(interaction.user.id)
        if user_id != match['player2_id']:
            await interaction.response.send_message("❌ Only the challenged player can accept this match", ephemeral=True)
            return
            
        if match['status'] != 'pending':
            await interaction.response.send_message("❌ This match is no longer pending", ephemeral=True)
            return
        
        # Update match status
        self.db.update_match_status(match_id, 'accepted')
        
        embed = discord.Embed(
            title="✅ Match Accepted!",
            description=f"Match `{match_id}` has been accepted and is now confirmed",
            color=0x43B581
        )
        
        embed.add_field(
            name="⚔️ Fighters",
            value=f"<@{match['player1_id']}> vs <@{match['player2_id']}>",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="decline_match", description="Decline a match challenge")
    @app_commands.describe(match_id="Match ID to decline")
    async def decline_match(self, interaction: discord.Interaction, match_id: str):
        """Decline a match challenge"""
        match = self.db.get_match(match_id)
        
        if not match:
            await interaction.response.send_message(f"❌ No match found with ID `{match_id}`", ephemeral=True)
            return
            
        user_id = str(interaction.user.id)
        if user_id != match['player2_id']:
            await interaction.response.send_message("❌ Only the challenged player can decline this match", ephemeral=True)
            return
        
        # Update match status
        self.db.update_match_status(match_id, 'declined')
        
        embed = discord.Embed(
            title="❌ Match Declined",
            description=f"Match `{match_id}` has been declined",
            color=0xF04747
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="report_result", description="Report match result")
    @app_commands.describe(
        match_id="Match ID",
        winner="Winner of the match",
        loser="Loser of the match"
    )
    async def report_result(
        self, 
        interaction: discord.Interaction, 
        match_id: str,
        winner: discord.Member,
        loser: discord.Member
    ):
        """Report match result"""
        match = self.db.get_match(match_id)
        
        if not match:
            await interaction.response.send_message(f"❌ No match found with ID `{match_id}`", ephemeral=True)
            return
        
        # Verify the users are part of this match
        player1_id = match['player1_id']
        player2_id = match['player2_id']
        winner_id = str(winner.id)
        loser_id = str(loser.id)
        
        if not ((winner_id == player1_id and loser_id == player2_id) or 
                (winner_id == player2_id and loser_id == player1_id)):
            await interaction.response.send_message("❌ Invalid players for this match", ephemeral=True)
            return
        
        # Update player statistics
        self.db.record_match_result(winner_id, loser_id, match_id)
        
        embed = discord.Embed(
            title="🏆 Match Result Recorded!",
            description=f"Match `{match_id}` result has been recorded",
            color=0xFFD700,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🥇 Winner",
            value=winner.mention,
            inline=True
        )
        
        embed.add_field(
            name="🥈 Loser", 
            value=loser.mention,
            inline=True
        )
        
        embed.set_footer(text="DUEL LORDS • Statistics updated!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="my_matches", description="View your upcoming and recent matches")
    async def my_matches(self, interaction: discord.Interaction):
        """View user's matches"""
        user_id = str(interaction.user.id)
        matches = self.db.get_player_matches(user_id)
        
        if not matches:
            await interaction.response.send_message("❌ You have no matches scheduled", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚔️ Your Matches",
            description=f"Matches for {interaction.user.display_name}",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        upcoming = []
        recent = []
        
        for match in matches:
            if match['status'] in ['scheduled', 'pending']:
                upcoming.append(match)
            else:
                recent.append(match)
        
        if upcoming:
            upcoming_text = ""
            for match in upcoming[:5]:
                opponent_id = match['player2_id'] if match['player1_id'] == user_id else match['player1_id']
                scheduled_time = datetime.fromisoformat(match['scheduled_time'])
                upcoming_text += f"vs <@{opponent_id}> - <t:{int(scheduled_time.timestamp())}:R>\n"
            
            embed.add_field(
                name="🔜 Upcoming Matches",
                value=upcoming_text,
                inline=False
            )
        
        if recent:
            recent_text = ""
            for match in recent[:3]:
                opponent_id = match['player2_id'] if match['player1_id'] == user_id else match['player1_id']
                status = match['status']
                recent_text += f"vs <@{opponent_id}> - {status.title()}\n"
            
            embed.add_field(
                name="📋 Recent Matches",
                value=recent_text,
                inline=False
            )
        
        embed.set_footer(text="DUEL LORDS • Stay competitive!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="all_matches", description="View all recent matches")
    async def all_matches(self, interaction: discord.Interaction):
        """View all recent matches"""
        matches = self.db.get_recent_matches(limit=10)
        
        if not matches:
            await interaction.response.send_message("❌ No recent matches found", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚔️ Recent Matches",
            description="Latest tournament activity",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        matches_text = ""
        for i, match in enumerate(matches, 1):
            player1_data = self.db.get_player(match['player1_id'])
            player2_data = self.db.get_player(match['player2_id'])
            
            name1 = player1_data.get('name', 'Unknown') if player1_data else 'Unknown'
            name2 = player2_data.get('name', 'Unknown') if player2_data else 'Unknown'
            
            status = match['status'].title()
            matches_text += f"`{i}.` **{name1}** vs **{name2}** - {status}\n"
        
        embed.add_field(
            name="📊 Match History",
            value=matches_text,
            inline=False
        )
        
        embed.set_footer(text="DUEL LORDS • Tournament activity")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MissingCommands(bot))