"""
Enhanced Embeds for DUEL LORDS Discord Bot
Beautiful Arabic-first embeds with comprehensive formatting
"""

import discord
from datetime import datetime

def create_duel_reminder_embed(match):
    """Create reminder embed for upcoming duel"""
    scheduled_time = datetime.fromisoformat(match['scheduled_time'])
    
    embed = discord.Embed(
        title="⏰ تذكير مبارزة!",
        description="مبارزتك تبدأ خلال 5 دقائق!",
        color=0xFF6B35,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="⚔️ المبارزة",
        value=f"<@{match['player1_id']}> **VS** <@{match['player2_id']}>",
        inline=False
    )
    
    embed.add_field(
        name="🕐 الموعد",
        value=f"<t:{int(scheduled_time.timestamp())}:F>",
        inline=True
    )
    
    embed.add_field(
        name="🌐 الخادم",
        value="**IP:** `18.228.228.44`\n**Port:** `3827`",
        inline=True
    )
    
    embed.add_field(
        name="📝 تعليمات",
        value="• ادخل إلى لعبة BombSquad الآن\n• اتصل بالخادم\n• استعد للمعركة!",
        inline=False
    )
    
    embed.set_footer(text="DUEL LORDS • حان وقت المعركة!")
    
    return embed

def create_duel_start_embed(match):
    """Create embed for duel start notification"""
    embed = discord.Embed(
        title="🚀 بدء المبارزة الآن!",
        description="المبارزة بدأت! اذهبوا إلى الخادم فوراً",
        color=0x43B581,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="⚔️ المتبارزون",
        value=f"<@{match['player1_id']}> **VS** <@{match['player2_id']}>",
        inline=False
    )
    
    embed.add_field(
        name="🌐 معلومات الاتصال",
        value="**IP:** `18.228.228.44`\n**Port:** `3827`",
        inline=True
    )
    
    embed.add_field(
        name="🏆 المكافأة",
        value="الفائز يحصل على نقاط انتصار",
        inline=True
    )
    
    embed.set_footer(text="DUEL LORDS • ليفز أفضل المقاتلين!")
    
    return embed

def create_leaderboard_embed(players):
    """Create an embed for the leaderboard"""
    embed = discord.Embed(
        title="🏆 Tournament Leaderboard",
        description="Top players ranked by wins and K/D ratio",
        color=discord.Color.gold()
    )
    
    if not players:
        embed.add_field(
            name="No Players",
            value="No players registered yet. Use `/register` to join!",
            inline=False
        )
        return embed
    
    leaderboard_text = ""
    for i, player in enumerate(players[:10], 1):
        kd_ratio = player['kills'] / max(player['deaths'], 1)
        win_rate = (player['wins'] / max(player['wins'] + player['losses'], 1)) * 100
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} **{player['username']}**\n"
        leaderboard_text += f"   {player['wins']}W/{player['losses']}L ({win_rate:.1f}%) • K/D: {kd_ratio:.2f}\n\n"
    
    embed.add_field(name="Rankings", value=leaderboard_text, inline=False)
    embed.set_footer(text="Use /stats to view detailed statistics")
    
    return embed

def create_challenge_embed(challenger, opponent, match_time, description, match_id):
    """Create an embed for match challenges"""
    embed = discord.Embed(
        title="⚔️ Match Challenge",
        description=f"**{challenger.display_name}** has challenged **{opponent.display_name}**!",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="Match Details",
        value=f"**Time:** <t:{int(match_time.timestamp())}:F>\n"
              f"**Description:** {description}\n"
              f"**Match ID:** `{match_id}`",
        inline=False
    )
    
    embed.add_field(
        name="Server Info",
        value="**IP:** `18.228.228.44:3827`",
        inline=False
    )
    
    embed.add_field(
        name="Actions",
        value=f"• `/accept_challenge {match_id}` - Accept the challenge\n"
              f"• `/decline_challenge {match_id}` - Decline the challenge",
        inline=False
    )
    
    embed.set_footer(text="Challenge expires if not responded to within 24 hours")
    embed.timestamp = datetime.now()
    
    return embed

def create_match_embed(match_data, challenger, opponent):
    """Create an embed for match information"""
    embed = discord.Embed(
        title="🎮 Match Information",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Players",
        value=f"**{challenger.display_name}** vs **{opponent.display_name}**",
        inline=False
    )
    
    if match_data['scheduled_time']:
        scheduled_time = datetime.fromisoformat(match_data['scheduled_time'])
        embed.add_field(
            name="Scheduled Time",
            value=f"<t:{int(scheduled_time.timestamp())}:F>",
            inline=True
        )
    
    embed.add_field(name="Status", value=match_data['status'].title(), inline=True)
    embed.add_field(name="Description", value=match_data['description'], inline=True)
    
    return embed

def create_tournament_embed(tournament_data, bot):
    """Create an embed for tournament information"""
    embed = discord.Embed(
        title=f"🏆 {tournament_data['name']}",
        description=tournament_data['description'],
        color=discord.Color.gold()
    )
    
    status_colors = {
        'registration': discord.Color.green(),
        'active': discord.Color.orange(),
        'completed': discord.Color.red()
    }
    
    embed.color = status_colors.get(tournament_data['status'], discord.Color.blue())
    
    embed.add_field(
        name="Tournament Details",
        value=f"**ID:** {tournament_data['id']}\n"
              f"**Status:** {tournament_data['status'].title()}\n"
              f"**Players:** {len(tournament_data['participants'])}/{tournament_data['max_players']}",
        inline=True
    )
    
    if tournament_data['participants']:
        participant_names = []
        for user_id in tournament_data['participants'][:10]:  # Show first 10
            try:
                user = bot.get_user(int(user_id))
                if user:
                    participant_names.append(user.display_name)
            except:
                participant_names.append(f"User {user_id}")
        
        participants_text = "\n".join(participant_names)
        if len(tournament_data['participants']) > 10:
            participants_text += f"\n... and {len(tournament_data['participants']) - 10} more"
        
        embed.add_field(name="Participants", value=participants_text, inline=False)
    
    embed.timestamp = datetime.fromisoformat(tournament_data['created_at'])
    
    return embed

def create_bracket_embed(tournament_data, bot):
    """Create an embed for tournament bracket"""
    embed = discord.Embed(
        title=f"🏆 {tournament_data['name']} - Bracket",
        color=discord.Color.gold()
    )
    
    if not tournament_data.get('matches'):
        embed.add_field(
            name="No Matches",
            value="Tournament hasn't started yet or no matches generated.",
            inline=False
        )
        return embed
    
    bracket_text = ""
    for i, match in enumerate(tournament_data['matches'], 1):
        try:
            player1 = bot.get_user(int(match['player1']))
            player2 = bot.get_user(int(match['player2']))
            
            player1_name = player1.display_name if player1 else "Unknown"
            player2_name = player2.display_name if player2 else "Unknown"
            
            status_emoji = {
                'pending': '⏳',
                'active': '⚔️',
                'completed': '✅'
            }
            
            bracket_text += f"{status_emoji.get(match['status'], '❓')} **Match {i}:** {player1_name} vs {player2_name}\n"
            
        except Exception as e:
            bracket_text += f"❓ **Match {i}:** Error loading match\n"
    
    embed.add_field(name="Matches", value=bracket_text, inline=False)
    
    return embed

def create_server_info_embed():
    """Create an embed with server information"""
    embed = discord.Embed(
        title="🎮 BombSquad Tournament Server",
        description="Connect to our dedicated BombSquad server!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🌐 Server IP",
        value="`18.228.228.44:3827`",
        inline=False
    )
    
    embed.add_field(
        name="📱 How to Connect",
        value="1. Open BombSquad\n2. Go to **Multiplayer**\n3. Select **By Address**\n4. Enter the IP above\n5. Click **Connect**",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Tournament Features",
        value="• Dedicated tournament matches\n• Fair play monitoring\n• Match recording\n• Statistics tracking",
        inline=False
    )
    
    embed.set_footer(text="Good luck and have fun!")
    embed.timestamp = datetime.now()
    
    return embed

def create_help_embed():
    """Create an embed with help information"""
    embed = discord.Embed(
        title="🤖 BombSquad Tournament Bot - Commands",
        description="All available commands for the tournament system",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="👤 Player Commands",
        value="`/register` - Register for tournaments\n"
              "`/stats [player]` - View player statistics\n"
              "`/leaderboard` - View tournament rankings",
        inline=False
    )
    
    embed.add_field(
        name="⚔️ Match Commands",
        value="`/challenge @player time description` - Challenge a player\n"
              "`/accept_challenge match_id` - Accept a challenge\n"
              "`/decline_challenge match_id` - Decline a challenge",
        inline=False
    )
    
    embed.add_field(
        name="🏆 Tournament Commands",
        value="`/join_tournament tournament_id` - Join a tournament\n"
              "`/tournament_info tournament_id` - View tournament info",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Admin Commands",
        value="`/admin_match @p1 @p2 day hour minute` - Create match\n"
              "`/admin_update_stats` - Update player stats\n"
              "`/create_tournament` - Create new tournament",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ General Commands",
        value="`/server` - Server information\n"
              "`/ip` - Quick server IP\n"
              "`/help` - Show this help",
        inline=False
    )
    
    embed.set_footer(text="Use slash commands (/) to interact with the bot")
    
    return embed
