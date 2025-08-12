#!/usr/bin/env python3
"""
DUEL LORDS - Simple Discord Bot
Simplified version that works reliably
"""

import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple database functions
def load_data(filename):
    try:
        with open(f"data/{filename}", 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(filename, data):
    try:
        os.makedirs("data", exist_ok=True)
        with open(f"data/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")

# Bot class
class DuelLordsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        """Setup slash commands"""
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Bot ready event"""
        print(f'🎮 DUEL LORDS is online!')
        print(f'Bot: {self.user.name} (ID: {self.user.id})')
        print(f'Servers: {len(self.guilds)}')
        
        # List servers
        for guild in self.guilds:
            print(f'  - {guild.name} (ID: {guild.id}) - {guild.member_count} members')
        
        print('=' * 50)
        print('✅ Bot is ready and listening for slash commands!')
        print('Available commands: /register, /stats, /ip, /help, /ping, /leaderboard')
        print('=' * 50)
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="BombSquad Tournaments | /help"
            )
        )

# Create bot instance
bot = DuelLordsBot()

# Register command
@bot.tree.command(name="register", description="Register for the tournament")
@app_commands.describe(name="Your player name (optional)")
async def register(interaction: discord.Interaction, name: str = None):
    """Register a new player"""
    user = interaction.user
    player_name = name or user.display_name
    
    players = load_data("players.json")
    
    if str(user.id) in players:
        embed = discord.Embed(
            title="❌ Already Registered",
            description=f"You are already registered, **{player_name}**!",
            color=0xF04747
        )
    else:
        players[str(user.id)] = {
            'name': player_name,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'kills': 0,
            'deaths': 0,
            'registered_at': datetime.now().isoformat()
        }
        save_data("players.json", players)
        
        embed = discord.Embed(
            title="✅ Registration Successful!",
            description=f"Welcome to the tournament, **{player_name}**!",
            color=0x43B581
        )
    
    await interaction.response.send_message(embed=embed)

# Stats command
@bot.tree.command(name="stats", description="Show player statistics")
@app_commands.describe(player="Player to show stats for (optional)")
async def stats(interaction: discord.Interaction, player: discord.Member = None):
    """Show player statistics"""
    target = player or interaction.user
    players = load_data("players.json")
    
    player_data = players.get(str(target.id))
    
    if not player_data:
        embed = discord.Embed(
            title="❌ Player Not Found",
            description=f"{target.mention} is not registered. Use `/register` to join!",
            color=0xF04747
        )
    else:
        wins = player_data.get('wins', 0)
        losses = player_data.get('losses', 0)
        draws = player_data.get('draws', 0)
        kills = player_data.get('kills', 0)
        deaths = player_data.get('deaths', 0)
        
        total_matches = wins + losses + draws
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        kd_ratio = (kills / deaths) if deaths > 0 else kills
        
        embed = discord.Embed(
            title=f"🏆 Stats: {player_data['name']}",
            color=0x007bff
        )
        embed.add_field(name="Wins", value=str(wins), inline=True)
        embed.add_field(name="Losses", value=str(losses), inline=True)
        embed.add_field(name="Draws", value=str(draws), inline=True)
        embed.add_field(name="Kills", value=str(kills), inline=True)
        embed.add_field(name="Deaths", value=str(deaths), inline=True)
        embed.add_field(name="K/D Ratio", value=f"{kd_ratio:.2f}", inline=True)
        embed.add_field(name="Win Rate", value=f"{win_rate:.1f}%", inline=True)
        embed.add_field(name="Total Matches", value=str(total_matches), inline=True)
    
    await interaction.response.send_message(embed=embed)

# IP command
@bot.tree.command(name="ip", description="Show BombSquad server information")
async def server_ip(interaction: discord.Interaction):
    """Show server IP"""
    embed = discord.Embed(
        title="🌐 BombSquad Server",
        description="**IP:** `18.228.228.44:3827`",
        color=0x00D4FF
    )
    embed.add_field(
        name="How to Connect",
        value="1. Open BombSquad\n2. Go to Play → Network\n3. Enter IP: `18.228.228.44:3827`\n4. Click Connect",
        inline=False
    )
    await interaction.response.send_message(embed=embed)

# Help command
@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help"""
    embed = discord.Embed(
        title="🤖 DUEL LORDS Commands",
        description="BombSquad Tournament Bot Commands",
        color=0x7C4DFF
    )
    
    commands_list = [
        "`/register` - Register for tournament",
        "`/stats` - Show your statistics",
        "`/ip` - Show server information",
        "`/help` - Show this help",
        "`/ping` - Check bot latency",
        "`/leaderboard` - Show top players"
    ]
    
    embed.add_field(
        name="Available Commands",
        value="\n".join(commands_list),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# Ping command
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=0x00FF00
    )
    await interaction.response.send_message(embed=embed)

# Leaderboard command
@bot.tree.command(name="leaderboard", description="Show top players")
@app_commands.describe(stat="Statistic to sort by")
@app_commands.choices(stat=[
    app_commands.Choice(name="Wins", value="wins"),
    app_commands.Choice(name="Kills", value="kills"),
    app_commands.Choice(name="K/D Ratio", value="kd")
])
async def leaderboard(interaction: discord.Interaction, stat: str = "wins"):
    """Show leaderboard"""
    players = load_data("players.json")
    
    if not players:
        embed = discord.Embed(
            title="📊 Leaderboard",
            description="No players registered yet!",
            color=0xF04747
        )
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
        title=f"🏆 {stat.title()} Leaderboard",
        color=0xFFD700
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
    
    embed.add_field(
        name="Top Players",
        value=leaderboard_text or "No data available",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

async def main():
    """Main function to run the bot"""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ DISCORD_TOKEN not found!")
        return
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Bot error: {e}")
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())