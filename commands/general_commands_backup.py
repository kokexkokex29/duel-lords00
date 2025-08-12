"""
General Commands for DUEL LORDS Discord Bot
Information commands, help, and utility functions
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="ip", description="Show BombSquad server information")
    async def server_ip(self, interaction: discord.Interaction):
        """Show BombSquad server information"""
        embed = discord.Embed(
            title="🌐 BombSquad Server Information",
            description="Official game server connection details",
            color=0x00D4FF,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🔗 IP Address",
            value="```18.228.228.44```",
            inline=True
        )
        
        embed.add_field(
            name="🔌 Port",
            value="```3827```",
            inline=True
        )
        
        embed.add_field(
            name="📋 How to Connect",
            value="1. Open BombSquad\n"
                  "2. Go to Play > Network\n"
                  "3. Enter IP and Port\n"
                  "4. Click Connect",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Important Notes",
            value="• Ensure stable internet connection\n"
                  "• Use latest game version\n"
                  "• Check firewall settings\n"
                  "• Retry if connection fails",
            inline=False
        )
        
        embed.set_footer(text="DUEL LORDS • See you in the arena!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show bot help information")
    async def help_command(self, interaction: discord.Interaction):
        """Show bot help information"""
        embed = discord.Embed(
            title="🤖 DUEL LORDS Commands Guide",
            description="Advanced Discord bot for BombSquad tournament management with smart duel system",
            color=0x7289DA,
            timestamp=datetime.now()
        )
        
        # Player commands
        embed.add_field(
            name="👥 Player Commands",
            value="`/register` - Register new player\n"
                  "`/stats` - Show player statistics\n"
                  "`/players` - Show all players\n"
                  "`/fighters` - Show top fighters",
            inline=True
        )
        
        # Match commands
        embed.add_field(
            name="⚔️ Duel Commands",
            value="`/duel` - Challenge players to a duel\n"
                  "`/record_result` - Record duel result\n"
                  "`/matches` - Show scheduled matches\n"
                  "`/cancel_match` - Cancel a match",
            inline=True
        )
        
        # Info commands
        embed.add_field(
            name="ℹ️ Information Commands",
            value="`/ip` - Show server information\n"
                  "`/help` - Show this help\n"
                  "`/about` - About the bot\n"
                  "`/ping` - Check bot latency",
            inline=True
        )
        
        # Tournament commands
        embed.add_field(
            name="🏆 Tournament Commands",
            value="`/tournament` - Show tournament info\n"
                  "`/leaderboard` - Player rankings\n"
                  "`/kill_stats` - Kill statistics",
            inline=True
        )
        
        # Special features
        embed.add_field(
            name="✨ Special Features",
            value="• Automatic private messages for duels\n"
                  "• 5-minute match reminders\n"
                  "• Smart ranking system\n"
                  "• Detailed player statistics",
            inline=True
        )
        
        # Examples
        embed.add_field(
            name="💡 Usage Examples",
            value="`/duel @Player1 @Player2 20 30` - Duel at 8:30 PM\n"
                  "`/fighters kills 5` - Top 5 killers\n"
                  "`/stats @Player` - Specific player stats",
            inline=False
        )
        
        embed.set_footer(text="DUEL LORDS • For detailed help, contact admins")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="about", description="Information about the bot")
    async def about_bot(self, interaction: discord.Interaction):
        """Show information about the bot"""
        # Get statistics
        total_players = len(self.db.get_all_players())
        total_matches = len(self.db.get_all_matches())
        active_matches = len([m for m in self.db.get_all_matches().values() if m.get('status') == 'scheduled'])
        
        embed = discord.Embed(
            title="🤖 About DUEL LORDS",
            description="Advanced Discord bot for BombSquad tournament management with professional duel system",
            color=0xFFD700,
            timestamp=datetime.now()
        )
        
        # Bot statistics
        embed.add_field(
            name="📊 Bot Statistics",
            value=f"🏠 **Servers:** {len(self.bot.guilds)}\n"
                  f"👥 **Players:** {total_players}\n"
                  f"⚔️ **Duels:** {total_matches}\n"
                  f"🔄 **Active:** {active_matches}",
            inline=True
        )
        
        # Features
        embed.add_field(
            name="✨ Key Features",
            value="• Player registration & management\n"
                  "• Smart duel system\n"
                  "• Automatic reminders\n"
                  "• Private player messages\n"
                  "• Comprehensive statistics\n"
                  "• Dynamic rankings",
            inline=True
        )
        
        # Technical info
        embed.add_field(
            name="🔧 Technical Information",
            value=f"• **Language:** Python 3.11\n"
                  f"• **Library:** discord.py\n"
                  f"• **Version:** 2.0\n"
                  f"• **Uptime:** <t:{int(datetime.now().timestamp())}:R>",
            inline=True
        )
        
        # Server info
        embed.add_field(
            name="🌐 Game Server",
            value="**IP:** `18.228.228.44`\n**Port:** `3827`\n**Status:** 🟢 Available",
            inline=True
        )
        
        # Commands count
        total_commands = len([cmd for cmd in self.bot.tree.walk_commands()])
        embed.add_field(
            name="⚡ System",
            value=f"**{total_commands}** slash commands available\n"
                  f"**24/7** continuous operation\n"
                  f"**Keep-alive** active",
            inline=True
        )
        
        # Credits
        embed.add_field(
            name="👨‍💻 Development",
            value="Developed with ❤️ for the BombSquad community",
            inline=True
        )
        
        embed.set_footer(
            text="DUEL LORDS • Professional Tournament Management Bot",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping", description="Check bot response latency")
    async def ping_command(self, interaction: discord.Interaction):
        """Check bot latency"""
        # Calculate latency
        latency = round(self.bot.latency * 1000)
        
        # Determine status based on latency
        if latency < 100:
            status = "🟢 Excellent"
            color = 0x43B581
        elif latency < 300:
            status = "🟡 Good"
            color = 0xFAA61A
        else:
            status = "🔴 Slow"
            color = 0xF04747
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Response time: **{latency}ms**",
            color=color,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 Status",
            value=status,
            inline=True
        )
        
        embed.add_field(
            name="🕐 Time",
            value=f"<t:{int(datetime.now().timestamp())}:T>",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bot",
            value="🟢 Connected & Active",
            inline=True
        )
        
        embed.set_footer(text="DUEL LORDS • Connection Check")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kill_stats", description="إحصائيات القتل في البطولة")
    async def kill_statistics(self, interaction: discord.Interaction):
        """Show kill statistics for the tournament"""
        players = self.db.get_all_players()
        
        if not players:
            embed = discord.Embed(
                title="📭 لا توجد إحصائيات",
                description="لم يتم تسجيل أي لاعبين بعد",
                color=0xF04747
            )
            await interaction.response.send_message(embed=embed)
            return

        # Calculate total kills and deaths
        total_kills = sum(player.get('kills', 0) for player in players.values())
        total_deaths = sum(player.get('deaths', 0) for player in players.values())
        total_matches = len([m for m in self.db.get_all_matches() if m.get('status') == 'completed'])
        
        # Top killers
        top_killers = sorted(players.items(), key=lambda x: x[1].get('kills', 0), reverse=True)[:5]
        
        # Best K/D ratios
        def get_kd_ratio(player_data):
            kills = player_data.get('kills', 0)
            deaths = player_data.get('deaths', 0)
            return kills / deaths if deaths > 0 else kills
        
        best_kd = sorted(players.items(), key=lambda x: get_kd_ratio(x[1]), reverse=True)[:5]
        
        embed = discord.Embed(
            title="⚔️ إحصائيات القتل - البطولة",
            description="إحصائيات شاملة للقتل والموت في البطولة",
            color=0xFF4444,
            timestamp=datetime.now()
        )
        
        # General statistics
        embed.add_field(
            name="📊 إحصائيات عامة",
            value=f"🔫 **إجمالي القتل:** {total_kills}\n"
                  f"💀 **إجمالي الموت:** {total_deaths}\n"
                  f"⚔️ **المباريات المكتملة:** {total_matches}\n"
                  f"📈 **متوسط القتل/مباراة:** {total_kills/total_matches:.1f}" if total_matches > 0 else "📈 **متوسط القتل/مباراة:** 0",
            inline=False
        )
        
        # Top killers
        killers_text = ""
        for i, (player_id, player_data) in enumerate(top_killers, 1):
            if i <= 3:
                medals = ["🥇", "🥈", "🥉"]
                rank = medals[i-1]
            else:
                rank = f"{i}."
            
            name = player_data.get('name', f'Player {player_id}')
            kills = player_data.get('kills', 0)
            killers_text += f"{rank} **{name}** - {kills} قتل\n"
        
        embed.add_field(
            name="🏆 أعلى قتل",
            value=killers_text if killers_text else "لا توجد بيانات",
            inline=True
        )
        
        # Best K/D
        kd_text = ""
        for i, (player_id, player_data) in enumerate(best_kd, 1):
            if i <= 3:
                medals = ["🥇", "🥈", "🥉"]
                rank = medals[i-1]
            else:
                rank = f"{i}."
            
            name = player_data.get('name', f'Player {player_id}')
            kd_ratio = get_kd_ratio(player_data)
            kd_text += f"{rank} **{name}** - {kd_ratio:.2f} K/D\n"
        
        embed.add_field(
            name="📈 أفضل نسبة K/D",
            value=kd_text if kd_text else "لا توجد بيانات",
            inline=True
        )
        
        embed.set_footer(text="DUEL LORDS • إحصائيات محدثة")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))