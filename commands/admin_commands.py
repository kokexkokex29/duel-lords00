import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timedelta
from utils.embeds import create_match_embed
from utils.translations import get_translation

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    def is_admin(self, interaction: discord.Interaction) -> bool:
        """Check if user has admin permissions"""
        # Check if user is a Member (has guild permissions) and is admin
        if isinstance(interaction.user, discord.Member) and interaction.user.guild_permissions:
            return interaction.user.guild_permissions.administrator
        return False

    @app_commands.command(name="admin_match", description="[ADMIN] Create a match between two players")
    @app_commands.describe(
        player1="First player in the match",
        player2="Second player in the match",
        day="Day of the month (1-31)",
        hour="Hour (0-23)",
        minute="Minute (0-59)",
        description="Match description"
    )
    async def admin_create_match(
        self, 
        interaction: discord.Interaction, 
        player1: discord.Member,
        player2: discord.Member,
        day: int,
        hour: int,
        minute: int,
        description: str = "Admin Match"
    ):
        """Create a match between two players with automatic date determination"""
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                get_translation('errors.missing_permissions'), 
                ephemeral=True
            )
            return

        try:
            # Validate inputs
            if day < 1 or day > 31:
                await interaction.response.send_message("❌ Day must be between 1 and 31", ephemeral=True)
                return
            
            if hour < 0 or hour > 23:
                await interaction.response.send_message("❌ Hour must be between 0 and 23", ephemeral=True)
                return
            
            if minute < 0 or minute > 59:
                await interaction.response.send_message("❌ Minute must be between 0 and 59", ephemeral=True)
                return

            # Check if both players are registered
            player1_id = str(player1.id)
            player2_id = str(player2.id)
            
            if not self.db.get_player(player1_id):
                await interaction.response.send_message(
                    f"❌ {player1.mention} is not registered. They need to use `/register` first.", 
                    ephemeral=True
                )
                return
            
            if not self.db.get_player(player2_id):
                await interaction.response.send_message(
                    f"❌ {player2.mention} is not registered. They need to use `/register` first.", 
                    ephemeral=True
                )
                return
            
            if player1_id == player2_id:
                await interaction.response.send_message("❌ Cannot create a match with the same player", ephemeral=True)
                return

            # Determine the correct date (current month/year, next month if day has passed)
            now = datetime.now()
            current_year = now.year
            current_month = now.month
            
            # Try to create the date for this month
            try:
                match_date = datetime(current_year, current_month, day, hour, minute)
                
                # If the date is in the past, move to next month
                if match_date <= now:
                    if current_month == 12:
                        match_date = datetime(current_year + 1, 1, day, hour, minute)
                    else:
                        match_date = datetime(current_year, current_month + 1, day, hour, minute)
                        
            except ValueError:
                # Invalid date (e.g., Feb 30), try next month
                if current_month == 12:
                    match_date = datetime(current_year + 1, 1, day, hour, minute)
                else:
                    try:
                        match_date = datetime(current_year, current_month + 1, day, hour, minute)
                    except ValueError:
                        await interaction.response.send_message("❌ Invalid date. Please check the day value.", ephemeral=True)
                        return

            # Create the match
            match_id = self.db.create_match(
                challenger_id=player1_id,
                opponent_id=player2_id,
                scheduled_time=match_date.isoformat(),
                description=description
            )

            # Set match status to accepted since it's admin created
            match_data = self.db.get_match(match_id)
            match_data['status'] = 'accepted'
            self.db.update_match(match_id, match_data)

            # Create embed
            embed = discord.Embed(
                title="🎮 Admin Match Created",
                description=f"**{player1.display_name}** vs **{player2.display_name}**",
                color=0xff6600
            )
            
            embed.add_field(
                name="Match Details",
                value=f"**Match ID:** `{match_id}`\n"
                      f"**Scheduled:** <t:{int(match_date.timestamp())}:F>\n"
                      f"**Description:** {description}",
                inline=False
            )
            
            embed.add_field(
                name="Server Info",
                value="**IP:** `18.228.228.44:3827`",
                inline=False
            )
            
            embed.add_field(
                name="Status",
                value="✅ **Confirmed** - Both players notified",
                inline=False
            )
            
            embed.set_footer(text=f"Created by {interaction.user.display_name}")
            embed.timestamp = datetime.now()

            # Send DM to both players
            dm_embed = discord.Embed(
                title="🎮 تم تحديد موعد مباراة لك | Match Scheduled",
                description=f"تم تحديد مباراة بينك وبين **{player2.display_name if interaction.user.id == player1.id else player1.display_name}**",
                color=0xff6600
            )
            
            dm_embed.add_field(
                name="📅 موعد المباراة | Match Time",
                value=f"<t:{int(match_date.timestamp())}:F>",
                inline=False
            )
            
            dm_embed.add_field(
                name="🎯 الوصف | Description",
                value=description,
                inline=False
            )
            
            dm_embed.add_field(
                name="🌐 خادم اللعبة | Game Server",
                value="**IP:** `18.228.228.44:3827`\n\nطريقة الاتصال:\n1. افتح BombSquad\n2. اختر Multiplayer\n3. أدخل العنوان أعلاه",
                inline=False
            )
            
            dm_embed.add_field(
                name="🏆 نوع المباراة | Match Type",
                value="مباراة إدارية - مؤكدة | Admin Match - Confirmed",
                inline=False
            )

            # Try to send DM to both players
            dm_sent_count = 0
            
            try:
                await player1.send(embed=dm_embed)
                dm_sent_count += 1
            except discord.Forbidden:
                logger.warning(f"Could not send DM to {player1.display_name}")
            except Exception as e:
                logger.error(f"Error sending DM to player1: {e}")
            
            try:
                await player2.send(embed=dm_embed)
                dm_sent_count += 1
            except discord.Forbidden:
                logger.warning(f"Could not send DM to {player2.display_name}")
            except Exception as e:
                logger.error(f"Error sending DM to player2: {e}")

            # Update status message based on DM success
            status_msg = f"✅ **Confirmed** - Both players notified"
            if dm_sent_count == 1:
                status_msg = f"✅ **Confirmed** - 1 player notified via DM"
            elif dm_sent_count == 0:
                status_msg = f"✅ **Confirmed** - Players notified in channel"
            else:
                status_msg = f"✅ **Confirmed** - Both players notified via DM"
            
            embed.set_field_at(2, name="Status", value=status_msg, inline=False)

            await interaction.response.send_message(
                content=f"{player1.mention} {player2.mention} - تم تحديد موعد مباراة! | Match scheduled!",
                embed=embed
            )

        except Exception as e:
            logger.error(f"Error creating admin match: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while creating the match.", 
                ephemeral=True
            )

    @app_commands.command(name="admin_update_stats", description="[ADMIN] Update player statistics")
    @app_commands.describe(
        player="Player to update",
        wins="Wins to add",
        losses="Losses to add",
        draws="Draws to add",
        kills="Kills to add",
        deaths="Deaths to add"
    )
    async def admin_update_stats(
        self, 
        interaction: discord.Interaction, 
        player: discord.Member,
        wins: int = 0,
        losses: int = 0,
        draws: int = 0,
        kills: int = 0,
        deaths: int = 0
    ):
        """Update player statistics"""
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                get_translation('errors.missing_permissions'), 
                ephemeral=True
            )
            return

        try:
            user_id = str(player.id)
            player_data = self.db.get_player(user_id)
            
            if not player_data:
                await interaction.response.send_message(
                    f"❌ {player.mention} is not registered.", 
                    ephemeral=True
                )
                return

            # Update stats
            old_stats = {
                'wins': player_data['wins'],
                'losses': player_data['losses'],
                'draws': player_data['draws'],
                'kills': player_data['kills'],
                'deaths': player_data['deaths']
            }

            player_data['wins'] += wins
            player_data['losses'] += losses
            player_data['draws'] += draws
            player_data['kills'] += kills
            player_data['deaths'] += deaths

            # Ensure no negative values
            for stat in ['wins', 'losses', 'draws', 'kills', 'deaths']:
                if player_data[stat] < 0:
                    player_data[stat] = 0

            self.db.update_player(user_id, player_data)

            # Create embed
            embed = discord.Embed(
                title="📊 Player Stats Updated",
                description=f"Statistics updated for **{player.display_name}**",
                color=0x00ff00
            )

            changes = []
            if wins != 0: changes.append(f"Wins: {old_stats['wins']} → {player_data['wins']} (+{wins})")
            if losses != 0: changes.append(f"Losses: {old_stats['losses']} → {player_data['losses']} (+{losses})")
            if draws != 0: changes.append(f"Draws: {old_stats['draws']} → {player_data['draws']} (+{draws})")
            if kills != 0: changes.append(f"Kills: {old_stats['kills']} → {player_data['kills']} (+{kills})")
            if deaths != 0: changes.append(f"Deaths: {old_stats['deaths']} → {player_data['deaths']} (+{deaths})")

            if changes:
                embed.add_field(name="Changes", value="\n".join(changes), inline=False)
            else:
                embed.add_field(name="Result", value="No changes made", inline=False)

            # Calculate new K/D ratio
            kd_ratio = player_data['kills'] / max(player_data['deaths'], 1)
            win_rate = (player_data['wins'] / max(player_data['wins'] + player_data['losses'], 1)) * 100

            embed.add_field(
                name="Current Stats",
                value=f"**K/D Ratio:** {kd_ratio:.2f}\n**Win Rate:** {win_rate:.1f}%",
                inline=True
            )

            embed.set_footer(text=f"Updated by {interaction.user.display_name}")
            embed.timestamp = datetime.now()

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"Error updating player stats: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while updating stats.", 
                ephemeral=True
            )

    @app_commands.command(name="admin_reset_player", description="[ADMIN] Reset player statistics")
    @app_commands.describe(player="Player to reset")
    async def admin_reset_player(self, interaction: discord.Interaction, player: discord.Member):
        """Reset player statistics"""
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                get_translation('errors.missing_permissions'), 
                ephemeral=True
            )
            return

        try:
            user_id = str(player.id)
            player_data = self.db.get_player(user_id)
            
            if not player_data:
                await interaction.response.send_message(
                    f"❌ {player.mention} is not registered.", 
                    ephemeral=True
                )
                return

            # Reset stats
            player_data['wins'] = 0
            player_data['losses'] = 0
            player_data['draws'] = 0
            player_data['kills'] = 0
            player_data['deaths'] = 0

            self.db.update_player(user_id, player_data)

            embed = discord.Embed(
                title="🔄 Player Stats Reset",
                description=f"All statistics have been reset for **{player.display_name}**",
                color=0xffa500
            )
            
            embed.set_footer(text=f"Reset by {interaction.user.display_name}")
            embed.timestamp = datetime.now()

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"Error resetting player: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while resetting player.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
