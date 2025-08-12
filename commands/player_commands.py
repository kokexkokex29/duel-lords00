"""
Player Commands for DUEL LORDS Discord Bot
Player registration, statistics, and profile management
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class PlayerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="register", description="Register a new player for the tournament")
    @app_commands.describe(name="Player name (optional - Discord name will be used if not specified)")
    async def register_player(self, interaction: discord.Interaction, name: str | None = None):
        """Register a new player in the tournament"""
        user = interaction.user
        player_name = name or user.display_name
        
        # Check if already registered
        if self.db.get_player(str(user.id)):
            embed = discord.Embed(
                title="❌ Already Registered",
                description=f"You are already registered for the tournament, **{player_name}**!",
                color=0xF04747
            )
            embed.add_field(
                name="💡 Tip",
                value="You can use `/stats` to view your statistics",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Register the player
        success = self.db.register_player(str(user.id), player_name)
        
        if success:
            embed = discord.Embed(
                title="✅ Registration Successful!",
                description=f"Welcome to the BombSquad tournament, **{player_name}**!",
                color=0x43B581,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🎮 Player Name",
                value=player_name,
                inline=True
            )
            
            embed.add_field(
                name="🆔 Discord ID",
                value=f"{user.mention}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Initial Statistics",
                value="🏆 **Wins:** 0\n💀 **Losses:** 0\n🤝 **Draws:** 0\n⚔️ **Kills:** 0",
                inline=False
            )
            
            embed.add_field(
                name="🚀 Next Steps",
                value="• Use `/stats` to view your statistics\n• Use `/duel` to challenge another player\n• Use `/ip` to get server information\n• Use `/fighters` to see top players",
                inline=False
            )
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
            embed.set_footer(text="DUEL LORDS • See you in the arena!")
            
        else:
            embed = discord.Embed(
                title="❌ Registration Failed",
                description="An error occurred during registration. Please try again.",
                color=0xF04747
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="Show player statistics")
    @app_commands.describe(player="Player to show stats for (optional)")
    async def player_stats(self, interaction: discord.Interaction, player: discord.Member | None = None):
        """Show player statistics"""
        target_user = player or interaction.user
        player_data = self.db.get_player(str(target_user.id))
        
        if not player_data:
            embed = discord.Embed(
                title="❌ Player Not Registered",
                description=f"{'You are not' if target_user == interaction.user else 'This player is not'} registered for the tournament",
                color=0xF04747
            )
            embed.add_field(
                name="📝 To Register",
                value="Use `/register` command to join the tournament",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            return

        # Calculate statistics
        wins = player_data.get('wins', 0)
        losses = player_data.get('losses', 0)
        draws = player_data.get('draws', 0)
        kills = player_data.get('kills', 0)
        deaths = player_data.get('deaths', 0)
        
        total_games = wins + losses + draws
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        kd_ratio = (kills / deaths) if deaths > 0 else kills
        
        # Determine rank
        rank = self.calculate_rank(player_data)
        
        embed = discord.Embed(
            title="👑 ملف اللاعب",
            color=0xFFD700,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🎮 اسم اللاعب",
            value=f"**{player_data.get('name', target_user.display_name)}**",
            inline=True
        )
        
        embed.add_field(
            name="🏅 الرتبة",
            value=rank,
            inline=True
        )
        
        embed.add_field(
            name="📊 معدل الفوز",
            value=f"{win_rate:.1f}%",
            inline=True
        )
        
        embed.add_field(
            name="🏆 الانتصارات",
            value=f"**{wins}** فوز",
            inline=True
        )
        
        embed.add_field(
            name="💀 الهزائم",
            value=f"**{losses}** هزيمة",
            inline=True
        )
        
        embed.add_field(
            name="🤝 التعادل",
            value=f"**{draws}** تعادل",
            inline=True
        )
        
        embed.add_field(
            name="⚔️ القتل",
            value=f"**{kills}** قتل",
            inline=True
        )
        
        embed.add_field(
            name="💀 الموت",
            value=f"**{deaths}** موت",
            inline=True
        )
        
        embed.add_field(
            name="📊 نسبة K/D",
            value=f"**{kd_ratio:.2f}**",
            inline=True
        )
        
        # Registration date
        reg_date = player_data.get('registered_at', datetime.now().isoformat())
        try:
            reg_datetime = datetime.fromisoformat(reg_date)
            formatted_date = reg_datetime.strftime("%Y/%m/%d")
        except:
            formatted_date = "غير محدد"
        
        embed.add_field(
            name="📅 تاريخ التسجيل",
            value=formatted_date,
            inline=False
        )
        
        embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else None)
        embed.set_footer(text="DUEL LORDS • إحصائيات مفصلة")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="players", description="عرض جميع اللاعبين المسجلين")
    async def list_players(self, interaction: discord.Interaction):
        """List all registered players"""
        players = self.db.get_all_players()
        
        if not players:
            embed = discord.Embed(
                title="📭 لا يوجد لاعبين",
                description="لم يتم تسجيل أي لاعبين بعد.\nاستخدم `/register` للتسجيل",
                color=0xFAA61A
            )
            await interaction.response.send_message(embed=embed)
            return

        # Sort players by wins
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('wins', 0), reverse=True)
        
        embed = discord.Embed(
            title="👥 قائمة اللاعبين المسجلين",
            description=f"إجمالي {len(players)} لاعب مسجل في البطولة",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        players_text = ""
        for i, (player_id, player_data) in enumerate(sorted_players[:15], 1):  # Show top 15
            name = player_data.get('name', f'Player {player_id}')
            wins = player_data.get('wins', 0)
            losses = player_data.get('losses', 0)
            
            # Rank emoji
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈"
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"{i}."
            
            players_text += f"{rank_emoji} **{name}** - {wins}W/{losses}L\n"
        
        embed.add_field(
            name="🏆 ترتيب اللاعبين (حسب الانتصارات)",
            value=players_text,
            inline=False
        )
        
        embed.set_footer(text=f"إجمالي {len(players)} لاعب • عرض أفضل 15 لاعب")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fighters", description="عرض أقوى المقاتلين")
    @app_commands.describe(
        category="فئة الترتيب",
        limit="عدد اللاعبين المراد عرضهم (افتراضي: 10)"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="الانتصارات", value="wins"),
        app_commands.Choice(name="عدد القتل", value="kills"),
        app_commands.Choice(name="نسبة K/D", value="kd_ratio"),
        app_commands.Choice(name="معدل الفوز", value="win_rate")
    ])
    async def top_fighters(self, interaction: discord.Interaction, category: str = "wins", limit: int = 10):
        """Show top fighters leaderboard"""
        if limit < 1 or limit > 25:
            limit = 10
        
        players = self.db.get_all_players()
        
        if not players:
            embed = discord.Embed(
                title="📭 لا يوجد مقاتلين",
                description="لم يتم تسجيل أي لاعبين بعد",
                color=0xF04747
            )
            await interaction.response.send_message(embed=embed)
            return

        # Sort based on category
        sorted_players = []
        if category == "wins":
            sorted_players = sorted(players.items(), key=lambda x: x[1].get('wins', 0), reverse=True)
        elif category == "kills":
            sorted_players = sorted(players.items(), key=lambda x: x[1].get('kills', 0), reverse=True)
        elif category == "kd_ratio":
            def get_kd_ratio(player_data):
                kills = player_data.get('kills', 0)
                deaths = player_data.get('deaths', 0)
                return kills / deaths if deaths > 0 else kills
            sorted_players = sorted(players.items(), key=lambda x: get_kd_ratio(x[1]), reverse=True)
        elif category == "win_rate":
            def get_win_rate(player_data):
                wins = player_data.get('wins', 0)
                losses = player_data.get('losses', 0)
                draws = player_data.get('draws', 0)
                total = wins + losses + draws
                return wins / total if total > 0 else 0
            sorted_players = sorted(players.items(), key=lambda x: get_win_rate(x[1]), reverse=True)
        else:
            sorted_players = sorted(players.items(), key=lambda x: x[1].get('wins', 0), reverse=True)

        category_names = {
            "wins": "Wins",
            "kills": "Kills",
            "kd_ratio": "K/D Ratio",
            "win_rate": "Win Rate"
        }

        embed = discord.Embed(
            title=f"🏆 Top Fighters - {category_names.get(category, category)}",
            description=f"Top {min(limit, len(sorted_players))} fighters by {category_names.get(category, category)}",
            color=0xFFD700,
            timestamp=datetime.now()
        )

        fighters_text = ""
        for i, (player_id, player_data) in enumerate(sorted_players[:limit], 1):
            # Get rank emoji
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈"
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"`{i}.`"

            name = player_data.get('name', f'Player {player_id}')

            # Format value based on category
            value = ""
            if category == "wins":
                value = f"{player_data.get('wins', 0)} wins"
            elif category == "kills":
                value = f"{player_data.get('kills', 0)} kills"
            elif category == "kd_ratio":
                kills = player_data.get('kills', 0)
                deaths = player_data.get('deaths', 0)
                kd = kills / deaths if deaths > 0 else kills
                value = f"{kd:.2f} K/D"
            elif category == "win_rate":
                wins = player_data.get('wins', 0)
                losses = player_data.get('losses', 0)
                draws = player_data.get('draws', 0)
                total = wins + losses + draws
                if total > 0:
                    win_rate = (wins / total) * 100
                    value = f"{win_rate:.1f}% ({total} matches)"
                else:
                    value = "0% (0 matches)"
            else:
                value = f"{player_data.get('wins', 0)} wins"

            fighters_text += f"{rank_emoji} **{name}** - {value}\n"

        embed.add_field(
            name="📊 Rankings",
            value=fighters_text or "No fighters found",
            inline=False
        )

        embed.set_footer(text=f"DUEL LORDS • Total: {len(players)} players")

        await interaction.response.send_message(embed=embed)

    def calculate_rank(self, player_data):
        """Calculate player rank based on performance"""
        wins = player_data.get('wins', 0)
        losses = player_data.get('losses', 0)
        draws = player_data.get('draws', 0)
        total_games = wins + losses + draws
        
        if total_games == 0:
            return "🆕 Rookie"
        
        win_rate = (wins / total_games) * 100
        
        if win_rate >= 80 and wins >= 10:
            return "👑 Legend"
        elif win_rate >= 70 and wins >= 8:
            return "💎 Master"
        elif win_rate >= 60 and wins >= 5:
            return "🏆 Expert"
        elif win_rate >= 50 and wins >= 3:
            return "⭐ Skilled"
        elif win_rate >= 30:
            return "📈 Average"
        else:
            return "🔰 Beginner"

async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))