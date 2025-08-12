#!/usr/bin/env python3
"""
Clan Lords |Bombsquad - Complete Discord Bot
All 15 commands with full functionality + Advanced Messaging System
"""

import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
from datetime import datetime, timedelta
import uuid
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database functions
def load_data(filename):
    try:
        os.makedirs("data", exist_ok=True)
        with open(f"data/{filename}", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(filename, data):
    try:
        os.makedirs("data", exist_ok=True)
        with open(f"data/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def generate_id():
    return str(uuid.uuid4())[:8]

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

class DuelLordsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.reminder_task_started = False

bot = DuelLordsBot()

@bot.event
async def on_ready():
    print(f'🎮 Clan Lords |Bombsquad is online!')
    print(f'Bot: {bot.user.name} (ID: {bot.user.id})')
    print(f'Servers: {len(bot.guilds)}')
    
    for guild in bot.guilds:
        print(f'  - {guild.name} ({guild.member_count} members)')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} commands')
        print('Available commands: /register, /stats, /players, /fighters, /duel, /record_result, /matches, /cancel_match, /ip, /help, /about, /ping, /tournament, /leaderboard, /kill_stats')
    except Exception as e:
        print(f'❌ Sync failed: {e}')
    
    # Start reminder task
    if not bot.reminder_task_started:
        duel_reminder_task.start()
        bot.reminder_task_started = True
        print('✅ Clan Lords reminder system started')
    
    await bot.change_presence(activity=discord.Game(name="Clan Lords |Bombsquad | /help"))
    print('✅ Bot ready with all 15 commands!')

@tasks.loop(minutes=1)
async def duel_reminder_task():
    """Check for upcoming duels and send reminders"""
    try:
        matches = load_data("matches.json")
        current_time = datetime.now()
        
        for match_id, match in matches.items():
            if match['status'] != 'scheduled':
                continue
                
            match_time = datetime.fromisoformat(match['scheduled_time'])
            time_diff = match_time - current_time
            
            # Send reminder 5 minutes before
            if timedelta(minutes=4, seconds=30) <= time_diff <= timedelta(minutes=5, seconds=30):
                if not match.get('reminder_sent', False):
                    await send_duel_reminder(match)
                    # Update reminder status
                    matches[match_id]['reminder_sent'] = True
                    save_data("matches.json", matches)
            
            # Start the duel if time has come
            elif time_diff.total_seconds() <= 0 and match['status'] == 'scheduled':
                await start_duel(match)
                matches[match_id]['status'] = 'in_progress'
                save_data("matches.json", matches)
                
    except Exception as e:
        logger.error(f"Error in duel reminder task: {e}")

async def send_duel_reminder(match):
    """Send duel reminder to both players"""
    try:
        scheduled_time = datetime.fromisoformat(match['scheduled_time'])
        
        # Create reminder embed
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
        
        embed.set_footer(text="Clan Lords |Bombsquad • حان وقت المعركة!")
        
        # Send to both players
        try:
            player1 = await bot.fetch_user(int(match['player1_id']))
            await player1.send(embed=embed)
            print(f"✅ تذكير أرسل إلى {player1.display_name}")
        except:
            print(f"❌ فشل إرسال تذكير إلى player1 {match['player1_id']}")
        
        try:
            player2 = await bot.fetch_user(int(match['player2_id']))
            await player2.send(embed=embed)
            print(f"✅ تذكير أرسل إلى {player2.display_name}")
        except:
            print(f"❌ فشل إرسال تذكير إلى player2 {match['player2_id']}")
            
    except Exception as e:
        logger.error(f"Error sending duel reminder: {e}")

async def start_duel(match):
    """Send duel start notification"""
    try:
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
        
        embed.set_footer(text="Clan Lords |Bombsquad • ليفز أفضل المقاتلين!")
        
        # Send to both players
        for player_id in [match['player1_id'], match['player2_id']]:
            try:
                player = await bot.fetch_user(int(player_id))
                await player.send(embed=embed)
                print(f"✅ إشعار بدء المبارزة أرسل إلى {player.display_name}")
            except:
                print(f"❌ فشل إرسال إشعار بدء المبارزة إلى {player_id}")
                
    except Exception as e:
        logger.error(f"Error sending duel start notification: {e}")

async def send_duel_notification_dm(player1, player2, scheduled_time, match_id):
    """Send private message notification about the duel"""
    embeds = []
    
    # Create embeds for both players
    for player, opponent in [(player1, player2), (player2, player1)]:
        embed = discord.Embed(
            title="🎮 New Duel Scheduled!",
            description=f"You have a scheduled duel against **{opponent.display_name}**",
            color=0x00FF00,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="⚔️ Opponent",
            value=f"{opponent.mention} ({opponent.display_name})",
            inline=True
        )

        embed.add_field(
            name="🕐 الموعد",
            value=f"<t:{int(scheduled_time.timestamp())}:F>",
            inline=True
        )

        embed.add_field(
            name="⏰ متبقي",
            value=f"<t:{int(scheduled_time.timestamp())}:R>",
            inline=True
        )

        embed.add_field(
            name="🌐 معلومات الاتصال",
            value="**IP:** `18.228.228.44`\n**Port:** `3827`",
            inline=False
        )

        embed.add_field(
            name="📝 تعليمات",
            value="• ادخل إلى لعبة BombSquad\n• اتصل بالخادم باستخدام المعلومات أعلاه\n• ستحصل على تذكير قبل المبارزة بـ 5 دقائق",
            inline=False
        )

        embed.add_field(
            name="🆔 معرف المبارزة",
            value=f"`{match_id}`",
            inline=False
        )

        embed.set_footer(text="Clan Lords |Bombsquad • حظاً موفقاً في المبارزة!")
        
        try:
            await player.send(embed=embed)
            print(f"✅ دعوة المبارزة أرسلت إلى {player.display_name}")
        except discord.Forbidden:
            print(f"❌ لا يمكن إرسال رسالة خاصة إلى {player.display_name}")
        except Exception as e:
            print(f"❌ خطأ في إرسال الرسالة الخاصة إلى {player.display_name}: {e}")

# 👥 Player Commands
@bot.tree.command(name="register", description="Register new player")
@app_commands.describe(name="Your player name (optional)")
async def register(interaction: discord.Interaction, name: str = None):
    user = interaction.user
    player_name = name or user.display_name
    
    players = load_data("players.json")
    
    if str(user.id) in players:
        embed = discord.Embed(
            title="❌ Already Registered",
            description=f"You are already registered, **{player_name}**!",
            color=0xF04747
        )
        embed.add_field(name="💡 Tip", value="Use `/stats` to view your statistics", inline=False)
    else:
        players[str(user.id)] = {
            'name': player_name,
            'wins': 0, 'losses': 0, 'draws': 0,
            'kills': 0, 'deaths': 0,
            'registered_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        save_data("players.json", players)
        
        embed = discord.Embed(
            title="✅ Registration Successful!",
            description=f"Welcome to the BombSquad tournament, **{player_name}**!",
            color=0x43B581,
            timestamp=datetime.now()
        )
        embed.add_field(name="🎮 Player Name", value=player_name, inline=True)
        embed.add_field(name="🆔 Discord ID", value=f"{user.mention}", inline=True)
        embed.add_field(name="📊 Initial Statistics", value="🏆 **Wins:** 0\n💀 **Losses:** 0\n🤝 **Draws:** 0\n⚔️ **Kills:** 0", inline=False)
        embed.add_field(name="🚀 Next Steps", value="• Use `/stats` to view statistics\n• Use `/duel` to challenge players\n• Use `/ip` for server info", inline=False)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="Show player statistics")
@app_commands.describe(player="Player to show stats for (optional)")
async def stats(interaction: discord.Interaction, player: discord.Member = None):
    target = player or interaction.user
    players = load_data("players.json")
    data = players.get(str(target.id))
    
    if not data:
        embed = discord.Embed(
            title="❌ Player Not Found",
            description=f"{target.mention} is not registered. Use `/register` to join!",
            color=0xF04747
        )
    else:
        wins = data.get('wins', 0)
        losses = data.get('losses', 0)
        draws = data.get('draws', 0)
        kills = data.get('kills', 0)
        deaths = data.get('deaths', 0)
        
        total_matches = wins + losses + draws
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        kd_ratio = (kills / deaths) if deaths > 0 else kills
        
        embed = discord.Embed(
            title=f"🏆 Player Statistics: {data['name']}",
            description=f"Complete performance overview",
            color=0x007bff,
            timestamp=datetime.now()
        )
        embed.add_field(name="📊 Match Record", value=f"**Wins:** {wins}\n**Losses:** {losses}\n**Draws:** {draws}\n**Total:** {total_matches}", inline=True)
        embed.add_field(name="⚔️ Combat Stats", value=f"**Kills:** {kills}\n**Deaths:** {deaths}\n**K/D Ratio:** {kd_ratio:.2f}", inline=True)
        embed.add_field(name="📈 Performance", value=f"**Win Rate:** {win_rate:.1f}%\n**Registered:** {data.get('registered_at', 'Unknown')[:10]}", inline=True)
        embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot")
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="players", description="Show all players")
async def players(interaction: discord.Interaction):
    players = load_data("players.json")
    
    if not players:
        embed = discord.Embed(title="📋 Registered Players", description="No players registered yet!", color=0xF04747)
    else:
        embed = discord.Embed(title="📋 Registered Players", description=f"Total: {len(players)} players", color=0x00D4FF)
        
        player_list = ""
        for i, (user_id, data) in enumerate(players.items(), 1):
            player_list += f"{i}. **{data['name']}** - {data.get('wins', 0)}W/{data.get('losses', 0)}L\n"
            if i >= 20:  # Limit to 20 players
                player_list += f"... and {len(players) - 20} more players"
                break
        
        embed.add_field(name="Players List", value=player_list, inline=False)
        embed.set_footer(text="Use /register to join the tournament!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="fighters", description="Show top fighters")
@app_commands.describe(stat="Statistic to sort by", limit="Number of players to show")
@app_commands.choices(stat=[
    app_commands.Choice(name="Wins", value="wins"),
    app_commands.Choice(name="Kills", value="kills"),
    app_commands.Choice(name="K/D Ratio", value="kd")
])
async def fighters(interaction: discord.Interaction, stat: str = "wins", limit: int = 10):
    players = load_data("players.json")
    
    if not players:
        embed = discord.Embed(title="🏆 Top Fighters", description="No players registered yet!", color=0xF04747)
        await interaction.response.send_message(embed=embed)
        return
    
    # Convert to list and sort
    player_list = []
    for user_id, data in players.items():
        if stat == "kd":
            sort_value = (data.get('kills', 0) / data.get('deaths', 1)) if data.get('deaths', 0) > 0 else data.get('kills', 0)
        else:
            sort_value = data.get(stat, 0)
        player_list.append((data['name'], sort_value, user_id))
    
    player_list.sort(key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(
        title=f"🏆 Top {limit} Fighters - {stat.title()}",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    leaderboard_text = ""
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (name, value, user_id) in enumerate(player_list[:limit]):
        rank = i + 1
        medal = medals[i] if i < 3 else f"{rank}."
        
        if stat == "kd":
            value_str = f"{value:.2f}"
        else:
            value_str = str(int(value))
        
        leaderboard_text += f"{medal} **{name}** - {value_str}\n"
    
    embed.add_field(name="🏅 Rankings", value=leaderboard_text or "No data available", inline=False)
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot")
    
    await interaction.response.send_message(embed=embed)

# ⚔️ Duel Commands
@bot.tree.command(name="duel", description="Challenge players to a duel")
@app_commands.describe(
    player1="First player",
    player2="Second player", 
    hour="Hour (0-23)",
    minute="Minute (0-59)"
)
async def duel(interaction: discord.Interaction, player1: discord.Member, player2: discord.Member, hour: int, minute: int):
    # Validate time
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        embed = discord.Embed(title="❌ Invalid Time", description="Hour must be 0-23, minute must be 0-59", color=0xF04747)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Check if players are registered
    players = load_data("players.json")
    if str(player1.id) not in players:
        embed = discord.Embed(title="❌ Player Not Registered", description=f"{player1.mention} must register first!", color=0xF04747)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if str(player2.id) not in players:
        embed = discord.Embed(title="❌ Player Not Registered", description=f"{player2.mention} must register first!", color=0xF04747)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Create match
    matches = load_data("matches.json")
    match_id = generate_id()
    
    # Calculate scheduled time
    now = datetime.now()
    scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if scheduled <= now:
        scheduled += timedelta(days=1)
    
    match_data = {
        'id': match_id,
        'player1_id': str(player1.id),
        'player2_id': str(player2.id),
        'player1_name': players[str(player1.id)]['name'],
        'player2_name': players[str(player2.id)]['name'],
        'scheduled_time': scheduled.isoformat(),
        'status': 'scheduled',
        'created_at': datetime.now().isoformat(),
        'channel_id': str(interaction.channel.id),
        'challenger_id': str(interaction.user.id)
    }
    
    matches[match_id] = match_data
    save_data("matches.json", matches)
    
    embed = discord.Embed(
        title="⚔️ DUEL CHALLENGE CREATED!",
        description=f"**{match_data['player1_name']}** vs **{match_data['player2_name']}**",
        color=0xffc107,
        timestamp=datetime.now()
    )
    embed.add_field(name="🕐 Scheduled Time", value=f"**{scheduled.strftime('%Y-%m-%d %H:%M')}**", inline=True)
    embed.add_field(name="🆔 Match ID", value=f"`{match_id}`", inline=True)
    embed.add_field(name="🎮 Server Info", value="**IP:** `18.228.228.44:3827`\n**Game:** BombSquad", inline=False)
    embed.add_field(name="📝 Next Steps", value="• Both players will be notified\n• Join server at scheduled time\n• Use `/record_result` after match", inline=False)
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot")
    
    await interaction.response.send_message(f"🚨 **New Duel!** {player1.mention} vs {player2.mention}", embed=embed)
    
    # Send private messages to both players
    await send_duel_notification_dm(player1, player2, scheduled, match_id)

@bot.tree.command(name="record_result", description="Record duel result")
@app_commands.describe(
    match_id="Match ID",
    winner="Winner of the match (optional for draw)",
    player1_kills="Player 1 kills",
    player2_kills="Player 2 kills"
)
async def record_result(interaction: discord.Interaction, match_id: str, winner: discord.Member = None, player1_kills: int = 0, player2_kills: int = 0):
    matches = load_data("matches.json")
    
    if match_id not in matches:
        embed = discord.Embed(title="❌ Match Not Found", description=f"No match found with ID: `{match_id}`", color=0xF04747)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    match = matches[match_id]
    
    if match['status'] != 'scheduled':
        embed = discord.Embed(title="❌ Match Already Completed", description="This match has already been completed or cancelled", color=0xF04747)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Update match
    match['status'] = 'completed'
    match['completed_at'] = datetime.now().isoformat()
    match['player1_kills'] = player1_kills
    match['player2_kills'] = player2_kills
    match['winner_id'] = str(winner.id) if winner else None
    
    # Update player stats
    players = load_data("players.json")
    player1_id = match['player1_id']
    player2_id = match['player2_id']
    
    if winner:
        if str(winner.id) == player1_id:
            players[player1_id]['wins'] += 1
            players[player1_id]['kills'] += player1_kills
            players[player1_id]['deaths'] += player2_kills
            players[player2_id]['losses'] += 1
            players[player2_id]['kills'] += player2_kills
            players[player2_id]['deaths'] += player1_kills
        else:
            players[player2_id]['wins'] += 1
            players[player2_id]['kills'] += player2_kills
            players[player2_id]['deaths'] += player1_kills
            players[player1_id]['losses'] += 1
            players[player1_id]['kills'] += player1_kills
            players[player1_id]['deaths'] += player2_kills
    else:
        # Draw
        players[player1_id]['draws'] += 1
        players[player1_id]['kills'] += player1_kills
        players[player1_id]['deaths'] += player2_kills
        players[player2_id]['draws'] += 1
        players[player2_id]['kills'] += player2_kills
        players[player2_id]['deaths'] += player1_kills
    
    players[player1_id]['last_updated'] = datetime.now().isoformat()
    players[player2_id]['last_updated'] = datetime.now().isoformat()
    
    save_data("matches.json", matches)
    save_data("players.json", players)
    
    # Create result embed
    if winner:
        title = f"🏆 VICTORY! {players[str(winner.id)]['name']} Wins!"
        color = 0x43B581
    else:
        title = "🤝 DRAW! Great Fight!"
        color = 0x6c757d
    
    embed = discord.Embed(
        title=title,
        description=f"Match between **{match['player1_name']}** and **{match['player2_name']}** completed!",
        color=color,
        timestamp=datetime.now()
    )
    embed.add_field(name="📊 Final Score", value=f"**{match['player1_name']}:** {player1_kills} kills\n**{match['player2_name']}:** {player2_kills} kills", inline=True)
    embed.add_field(name="🆔 Match ID", value=f"`{match_id}`", inline=True)
    embed.add_field(name="📈 Stats Updated", value="Player statistics have been updated!", inline=False)
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="matches", description="Show scheduled matches")
async def matches(interaction: discord.Interaction):
    matches = load_data("matches.json")
    
    scheduled_matches = [m for m in matches.values() if m['status'] == 'scheduled']
    
    if not scheduled_matches:
        embed = discord.Embed(title="📅 Scheduled Matches", description="No scheduled matches found", color=0x6c757d)
    else:
        embed = discord.Embed(title="📅 Scheduled Matches", description=f"Total: {len(scheduled_matches)} matches", color=0x007bff)
        
        matches_text = ""
        for match in scheduled_matches[:10]:  # Show max 10
            time_str = datetime.fromisoformat(match['scheduled_time']).strftime('%m-%d %H:%M')
            matches_text += f"**{match['player1_name']}** vs **{match['player2_name']}**\n"
            matches_text += f"🕐 {time_str} | ID: `{match['id']}`\n\n"
        
        embed.add_field(name="Upcoming Matches", value=matches_text or "No matches", inline=False)
        embed.set_footer(text="Use /duel to create new matches")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cancel_match", description="Cancel a match")
@app_commands.describe(match_id="Match ID to cancel")
async def cancel_match(interaction: discord.Interaction, match_id: str):
    matches = load_data("matches.json")
    
    if match_id not in matches:
        embed = discord.Embed(title="❌ Match Not Found", color=0xF04747)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    match = matches[match_id]
    
    if match['status'] != 'scheduled':
        embed = discord.Embed(title="❌ Cannot Cancel", description="Match is not scheduled", color=0xF04747)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    matches[match_id]['status'] = 'cancelled'
    matches[match_id]['cancelled_at'] = datetime.now().isoformat()
    save_data("matches.json", matches)
    
    embed = discord.Embed(
        title="❌ Match Cancelled",
        description=f"Match between **{match['player1_name']}** and **{match['player2_name']}** has been cancelled",
        color=0xF04747
    )
    embed.add_field(name="Match ID", value=f"`{match_id}`", inline=True)
    
    await interaction.response.send_message(embed=embed)

# ℹ️ Information Commands
@bot.tree.command(name="ip", description="Show server information")
async def ip(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌐 BombSquad Server Information",
        description="Official Clan Lords |Bombsquad tournament server details",
        color=0x00D4FF,
        timestamp=datetime.now()
    )
    embed.add_field(name="🌐 Server Address", value="**IP:** `18.228.228.44`\n**Port:** `3827`", inline=True)
    embed.add_field(name="🎯 Connection", value="**Status:** Online ✅\n**Game:** BombSquad\n**Region:** Global", inline=True)
    embed.add_field(name="📋 How to Connect", value="1. Open BombSquad\n2. Go to 'Play' → 'Network'\n3. Enter IP: `18.228.228.44:3827`\n4. Join and start dueling!", inline=False)
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot • Official Server")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show this help")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Clan Lords |Bombsquad Commands Guide",
        description="Advanced Discord bot for BombSquad tournament management with smart duel system",
        color=0x7C4DFF,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="👥 Player Commands",
        value="`/register` - Register new player\n`/stats` - Show player statistics\n`/players` - Show all players\n`/fighters` - Show top fighters",
        inline=True
    )
    
    embed.add_field(
        name="⚔️ Duel Commands", 
        value="`/duel` - Challenge players to a duel\n`/record_result` - Record duel result\n`/matches` - Show scheduled matches\n`/cancel_match` - Cancel a match",
        inline=True
    )
    
    embed.add_field(
        name="ℹ️ Information Commands",
        value="`/ip` - Show server information\n`/help` - Show this help\n`/about` - About the bot\n`/ping` - Check bot latency",
        inline=True
    )
    
    embed.add_field(
        name="🏆 Tournament Commands",
        value="`/tournament` - Show tournament info\n`/leaderboard` - Player rankings\n`/kill_stats` - Kill statistics",
        inline=True
    )
    
    embed.add_field(
        name="✨ Special Features",
        value="• Automatic private messages for duels\n• Smart ranking system\n• Detailed player statistics\n• Match scheduling system",
        inline=True
    )
    
    embed.add_field(
        name="💡 Usage Examples",
        value="`/duel @Player1 @Player2 20 30` - Duel at 8:30 PM\n`/fighters kills 5` - Top 5 killers\n`/stats @Player` - Specific player stats",
        inline=True
    )
    
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot • Join the battle!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="about", description="About the bot")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 About Clan Lords |Bombsquad",
        description="Advanced Discord bot for BombSquad tournament management",
        color=0x7C4DFF,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🎮 Purpose",
        value="Manage BombSquad tournaments, duels, and player statistics with comprehensive features and automation",
        inline=False
    )
    
    embed.add_field(
        name="⚡ Features",
        value="• 15 Complete Commands\n• Player Registration & Stats\n• Duel Scheduling System\n• Tournament Management\n• Real-time Leaderboards\n• Match History Tracking",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Server Info",
        value="**Game:** BombSquad\n**Server:** 18.228.228.44:3827\n**Region:** Global\n**Status:** Online 24/7",
        inline=True
    )
    
    embed.add_field(
        name="📊 Statistics",
        value=f"**Players:** {len(load_data('players.json'))}\n**Matches:** {len(load_data('matches.json'))}\n**Uptime:** 24/7",
        inline=False
    )
    
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot • Built for competitive BombSquad")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    
    if latency < 100:
        color = 0x43B581
        status = "Excellent"
    elif latency < 200:
        color = 0xffc107
        status = "Good"
    else:
        color = 0xF04747
        status = "High"
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms** ({status})",
        color=color,
        timestamp=datetime.now()
    )
    embed.add_field(name="Response Time", value=f"{latency}ms", inline=True)
    embed.add_field(name="Status", value=f"✅ Online", inline=True)
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot")
    
    await interaction.response.send_message(embed=embed)

# 🏆 Tournament Commands
@bot.tree.command(name="tournament", description="Show tournament info")
async def tournament(interaction: discord.Interaction):
    players = load_data("players.json")
    matches = load_data("matches.json")
    
    completed_matches = [m for m in matches.values() if m['status'] == 'completed']
    scheduled_matches = [m for m in matches.values() if m['status'] == 'scheduled']
    
    embed = discord.Embed(
        title="🏆 Clan Lords |Bombsquad Tournament",
        description="BombSquad Tournament Information",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="👥 Registered Players", value=str(len(players)), inline=True)
    embed.add_field(name="⚔️ Total Matches", value=str(len(matches)), inline=True)
    embed.add_field(name="✅ Completed", value=str(len(completed_matches)), inline=True)
    embed.add_field(name="📅 Scheduled", value=str(len(scheduled_matches)), inline=True)
    embed.add_field(name="🎮 Game Server", value="18.228.228.44:3827", inline=True)
    embed.add_field(name="📊 Status", value="Active ✅", inline=True)
    
    if players:
        # Find top player
        top_player = max(players.values(), key=lambda x: x.get('wins', 0))
        embed.add_field(name="👑 Current Leader", value=f"**{top_player['name']}** ({top_player.get('wins', 0)} wins)", inline=False)
    
    embed.add_field(name="🚀 How to Join", value="Use `/register` to join the tournament and start dueling!", inline=False)
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="Player rankings")
@app_commands.describe(stat="Statistic to sort by")
@app_commands.choices(stat=[
    app_commands.Choice(name="Wins", value="wins"),
    app_commands.Choice(name="Kills", value="kills"),
    app_commands.Choice(name="K/D Ratio", value="kd")
])
async def leaderboard(interaction: discord.Interaction, stat: str = "wins"):
    players = load_data("players.json")
    
    if not players:
        embed = discord.Embed(title="📊 Leaderboard", description="No players registered yet!", color=0xF04747)
        await interaction.response.send_message(embed=embed)
        return
    
    # Convert to list and sort
    player_list = []
    for user_id, data in players.items():
        if stat == "kd":
            sort_value = (data.get('kills', 0) / data.get('deaths', 1)) if data.get('deaths', 0) > 0 else data.get('kills', 0)
        else:
            sort_value = data.get(stat, 0)
        player_list.append((data['name'], sort_value, user_id))
    
    player_list.sort(key=lambda x: x[1], reverse=True)
    
    stat_labels = {
        'wins': '🏆 Wins Leaderboard',
        'kills': '⚔️ Kills Leaderboard', 
        'kd': '📊 K/D Ratio Leaderboard'
    }
    
    embed = discord.Embed(
        title=stat_labels.get(stat, f'📈 {stat.title()} Leaderboard'),
        description=f"Top {min(len(player_list), 10)} fighters in the arena",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    leaderboard_text = ""
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (name, value, user_id) in enumerate(player_list[:10]):
        rank = i + 1
        medal = medals[i] if i < 3 else f"{rank}."
        
        if stat == "kd":
            value_str = f"{value:.2f}"
        else:
            value_str = str(int(value))
        
        leaderboard_text += f"{medal} **{name}** - {value_str}\n"
    
    embed.add_field(name="🏅 Rankings", value=leaderboard_text or "No players found", inline=False)
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot • Use /register to join!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kill_stats", description="Kill statistics")
async def kill_stats(interaction: discord.Interaction):
    players = load_data("players.json")
    
    if not players:
        embed = discord.Embed(title="⚔️ Kill Statistics", description="No players registered yet!", color=0xF04747)
        await interaction.response.send_message(embed=embed)
        return
    
    # Calculate stats
    total_kills = sum(p.get('kills', 0) for p in players.values())
    total_deaths = sum(p.get('deaths', 0) for p in players.values())
    total_matches = len([m for m in load_data("matches.json").values() if m['status'] == 'completed'])
    
    # Find top killer
    top_killer = max(players.values(), key=lambda x: x.get('kills', 0))
    
    # Find best K/D
    best_kd_player = max(players.values(), key=lambda x: (x.get('kills', 0) / x.get('deaths', 1)) if x.get('deaths', 0) > 0 else x.get('kills', 0))
    best_kd = (best_kd_player.get('kills', 0) / best_kd_player.get('deaths', 1)) if best_kd_player.get('deaths', 0) > 0 else best_kd_player.get('kills', 0)
    
    embed = discord.Embed(
        title="⚔️ Kill Statistics",
        description="Combat statistics across all matches",
        color=0xDC143C,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="📊 Global Stats", value=f"**Total Kills:** {total_kills}\n**Total Deaths:** {total_deaths}\n**Total Matches:** {total_matches}", inline=True)
    embed.add_field(name="🎯 Averages", value=f"**Kills/Match:** {total_kills/total_matches if total_matches > 0 else 0:.1f}\n**K/D Ratio:** {total_kills/total_deaths if total_deaths > 0 else 0:.2f}", inline=True)
    embed.add_field(name="👑 Top Killer", value=f"**{top_killer['name']}**\n{top_killer.get('kills', 0)} kills", inline=True)
    embed.add_field(name="🏆 Best K/D Ratio", value=f"**{best_kd_player['name']}**\n{best_kd:.2f} ratio", inline=True)
    
    embed.set_footer(text="Clan Lords |Bombsquad Tournament Bot")
    
    await interaction.response.send_message(embed=embed)

# Run bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ No DISCORD_TOKEN found!")
        exit(1)
    
    print("🚀 Starting Clan Lords |Bombsquad Bot with ALL 15 commands...")
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Bot error: {e}")