import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import create_tournament_embed, create_bracket_embed
from utils.translations import get_translation
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TournamentCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="create_tournament", description="Create a new tournament")
    @app_commands.describe(
        name="Tournament name",
        description="Tournament description",
        max_players="Maximum number of players"
    )
    async def create_tournament(
        self, 
        interaction: discord.Interaction, 
        name: str,
        description: str = "BombSquad Tournament",
        max_players: int = 16
    ):
        """Create a new tournament"""
        # Check permissions
        if not (isinstance(interaction.user, discord.Member) and interaction.user.guild_permissions.administrator):
            await interaction.response.send_message(
                get_translation('errors.missing_permissions'), 
                ephemeral=True
            )
            return
        
        try:
            tournament_id = self.db.create_tournament(
                name=name,
                description=description,
                max_players=max_players,
                creator_id=str(interaction.user.id)
            )
            
            embed = discord.Embed(
                title="🏆 Tournament Created",
                description=f"**{name}** has been created!",
                color=0xffd700
            )
            embed.add_field(name="Description", value=description, inline=False)
            embed.add_field(name="Max Players", value=str(max_players), inline=True)
            embed.add_field(name="Status", value="Registration Open", inline=True)
            embed.add_field(name="Tournament ID", value=tournament_id, inline=True)
            embed.set_footer(text=f"Created by {interaction.user.display_name}")
            embed.timestamp = datetime.now()
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating tournament: {e}")
            await interaction.response.send_message(
                get_translation('errors.general'), 
                ephemeral=True
            )

    @app_commands.command(name="join_tournament", description="Join an active tournament")
    @app_commands.describe(tournament_id="Tournament ID to join")
    async def join_tournament(self, interaction: discord.Interaction, tournament_id: str):
        """Join a tournament"""
        user_id = str(interaction.user.id)
        
        try:
            # Check if player is registered
            if not self.db.get_player(user_id):
                await interaction.response.send_message(
                    get_translation('player.must_register'), 
                    ephemeral=True
                )
                return
            
            tournament = self.db.get_tournament(tournament_id)
            if not tournament:
                await interaction.response.send_message(
                    get_translation('tournament.not_found'), 
                    ephemeral=True
                )
                return
            
            if tournament['status'] != 'registration':
                await interaction.response.send_message(
                    get_translation('tournament.registration_closed'), 
                    ephemeral=True
                )
                return
            
            if len(tournament['participants']) >= tournament['max_players']:
                await interaction.response.send_message(
                    get_translation('tournament.full'), 
                    ephemeral=True
                )
                return
            
            if user_id in tournament['participants']:
                await interaction.response.send_message(
                    get_translation('tournament.already_joined'), 
                    ephemeral=True
                )
                return
            
            # Add player to tournament
            tournament['participants'].append(user_id)
            self.db.update_tournament(tournament_id, tournament)
            
            embed = discord.Embed(
                title="✅ Tournament Joined",
                description=f"You've successfully joined **{tournament['name']}**!",
                color=0x00ff00
            )
            embed.add_field(
                name="Players", 
                value=f"{len(tournament['participants'])}/{tournament['max_players']}", 
                inline=True
            )
            embed.add_field(name="Status", value="Registered", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error joining tournament: {e}")
            await interaction.response.send_message(
                get_translation('errors.general'), 
                ephemeral=True
            )

    @app_commands.command(name="tournament_info", description="View tournament information")
    @app_commands.describe(tournament_id="Tournament ID to view")
    async def tournament_info(self, interaction: discord.Interaction, tournament_id: str):
        """View tournament information"""
        try:
            tournament = self.db.get_tournament(tournament_id)
            if not tournament:
                await interaction.response.send_message(
                    get_translation('tournament.not_found'), 
                    ephemeral=True
                )
                return
            
            embed = create_tournament_embed(tournament, self.bot)
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting tournament info: {e}")
            await interaction.response.send_message(
                get_translation('errors.general'), 
                ephemeral=True
            )

    @app_commands.command(name="tournament", description="Show tournament information")
    async def show_tournament(self, interaction: discord.Interaction):
        """Show current tournament information"""
        tournaments = self.db.get_all_tournaments()
        
        if not tournaments:
            embed = discord.Embed(
                title="🏆 No Active Tournaments",
                description="No tournaments are currently active",
                color=0xFAA61A
            )
            embed.add_field(
                name="💡 Create Tournament",
                value="Administrators can use `/create_tournament` to start a new tournament",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Get the most recent active tournament
        active_tournaments = [t for t in tournaments.values() if t['status'] == 'registration']
        
        if not active_tournaments:
            embed = discord.Embed(
                title="🏆 No Registration Open",
                description="No tournaments are currently accepting registrations",
                color=0xFAA61A
            )
            await interaction.response.send_message(embed=embed)
            return
        
        tournament = active_tournaments[0]  # Get first active tournament
        
        embed = discord.Embed(
            title="🏆 Current Tournament",
            description=tournament['description'],
            color=0xFFD700,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📛 Tournament Name",
            value=tournament['name'],
            inline=True
        )
        
        embed.add_field(
            name="👥 Participants",
            value=f"{len(tournament['participants'])}/{tournament['max_players']}",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Status",
            value="Registration Open",
            inline=True
        )
        
        embed.add_field(
            name="🎯 How to Join",
            value=f"Use `/join_tournament {tournament['id']}`",
            inline=False
        )
        
        embed.set_footer(text="DUEL LORDS • Join the competition!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Show player rankings")
    @app_commands.describe(limit="Number of top players to show (1-20)")
    async def show_leaderboard(self, interaction: discord.Interaction, limit: int = 10):
        """Show player rankings leaderboard"""
        
        if limit < 1 or limit > 20:
            await interaction.response.send_message(
                "❌ Limit must be between 1 and 20",
                ephemeral=True
            )
            return
        
        players = self.db.get_all_players()
        
        if not players:
            embed = discord.Embed(
                title="📊 Empty Leaderboard",
                description="No players have registered yet",
                color=0xFAA61A
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Sort players by wins, then by kills
        sorted_players = sorted(
            players.values(),
            key=lambda p: (p.get('wins', 0), p.get('kills', 0)),
            reverse=True
        )
        
        embed = discord.Embed(
            title="🏆 Tournament Leaderboard",
            description=f"Top {min(limit, len(sorted_players))} players",
            color=0xFFD700,
            timestamp=datetime.now()
        )
        
        for i, player in enumerate(sorted_players[:limit], 1):
            try:
                user = await interaction.client.fetch_user(int(player['user_id']))
                name = user.display_name
            except:
                name = player.get('name', 'Unknown')
            
            wins = player.get('wins', 0)
            losses = player.get('losses', 0)
            kills = player.get('kills', 0)
            
            # Add position emoji
            if i == 1:
                position = "🥇"
            elif i == 2:
                position = "🥈"
            elif i == 3:
                position = "🥉"
            else:
                position = f"#{i}"
            
            embed.add_field(
                name=f"{position} {name}",
                value=f"🏆 {wins}W-{losses}L | ⚔️ {kills} kills",
                inline=True
            )
        
        embed.set_footer(text="DUEL LORDS • Climb the ranks!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kill_stats", description="Show kill statistics leaderboard")
    @app_commands.describe(limit="Number of top killers to show (1-20)")
    async def kill_statistics(self, interaction: discord.Interaction, limit: int = 10):
        """Show kill statistics leaderboard"""
        
        if limit < 1 or limit > 20:
            await interaction.response.send_message(
                "❌ Limit must be between 1 and 20",
                ephemeral=True
            )
            return
        
        players = self.db.get_all_players()
        
        if not players:
            embed = discord.Embed(
                title="⚔️ No Kill Stats",
                description="No players have recorded kills yet",
                color=0xFAA61A
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Sort players by kills, then by KD ratio
        sorted_players = sorted(
            players.values(),
            key=lambda p: (p.get('kills', 0), p.get('kills', 0) / max(p.get('deaths', 1), 1)),
            reverse=True
        )
        
        embed = discord.Embed(
            title="⚔️ Kill Statistics",
            description=f"Top {min(limit, len(sorted_players))} killers",
            color=0xFF4444,
            timestamp=datetime.now()
        )
        
        for i, player in enumerate(sorted_players[:limit], 1):
            try:
                user = await interaction.client.fetch_user(int(player['user_id']))
                name = user.display_name
            except:
                name = player.get('name', 'Unknown')
            
            kills = player.get('kills', 0)
            deaths = player.get('deaths', 0)
            kd_ratio = kills / max(deaths, 1)
            
            # Add rank emoji
            if i <= 3:
                rank_emoji = ["🥇", "🥈", "🥉"][i-1]
            else:
                rank_emoji = f"#{i}"
            
            embed.add_field(
                name=f"{rank_emoji} {name}",
                value=f"⚔️ **{kills}** kills\n💀 {deaths} deaths\n📊 {kd_ratio:.2f} K/D",
                inline=True
            )
        
        embed.set_footer(text="DUEL LORDS • Most lethal fighters!")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TournamentCommands(bot))
