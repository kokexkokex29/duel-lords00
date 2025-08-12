#!/usr/bin/env python3
"""
DUEL LORDS - Direct Discord Bot (No Guardian)
Simple bot that runs directly for testing
"""

import os
import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime

# Simple database functions
def load_players():
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/players.json", 'r') as f:
            return json.load(f)
    except:
        return {}

def save_players(data):
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/players.json", 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving: {e}")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'🎮 {bot.user.name} is online!')
    print(f'ID: {bot.user.id}')
    print(f'Servers: {len(bot.guilds)}')
    
    for guild in bot.guilds:
        print(f'  - {guild.name} ({guild.member_count} members)')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} commands')
    except Exception as e:
        print(f'❌ Sync failed: {e}')
    
    await bot.change_presence(activity=discord.Game(name="BombSquad Tournament | /help"))
    print('✅ Bot ready!')

# Commands
@bot.tree.command(name="register", description="Register for tournament")
async def register(interaction: discord.Interaction, name: str = None):
    user = interaction.user
    player_name = name or user.display_name
    
    players = load_players()
    
    if str(user.id) in players:
        embed = discord.Embed(title="❌ Already Registered", color=0xff0000)
    else:
        players[str(user.id)] = {
            'name': player_name,
            'wins': 0, 'losses': 0, 'draws': 0,
            'kills': 0, 'deaths': 0,
            'registered': datetime.now().isoformat()
        }
        save_players(players)
        embed = discord.Embed(title="✅ Registered!", description=f"Welcome {player_name}!", color=0x00ff00)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="Show statistics")
async def stats(interaction: discord.Interaction, player: discord.Member = None):
    target = player or interaction.user
    players = load_players()
    data = players.get(str(target.id))
    
    if not data:
        embed = discord.Embed(title="❌ Not Registered", color=0xff0000)
    else:
        embed = discord.Embed(title=f"📊 {data['name']}", color=0x0099ff)
        embed.add_field(name="Wins", value=data.get('wins', 0), inline=True)
        embed.add_field(name="Losses", value=data.get('losses', 0), inline=True)
        embed.add_field(name="Draws", value=data.get('draws', 0), inline=True)
        embed.add_field(name="Kills", value=data.get('kills', 0), inline=True)
        embed.add_field(name="Deaths", value=data.get('deaths', 0), inline=True)
        
        total = data.get('wins', 0) + data.get('losses', 0) + data.get('draws', 0)
        winrate = (data.get('wins', 0) / total * 100) if total > 0 else 0
        embed.add_field(name="Win Rate", value=f"{winrate:.1f}%", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ip", description="Server information")
async def ip(interaction: discord.Interaction):
    embed = discord.Embed(title="🌐 BombSquad Server", color=0x00ddff)
    embed.add_field(name="IP", value="18.228.228.44", inline=True)
    embed.add_field(name="Port", value="3827", inline=True)
    embed.add_field(name="Full Address", value="18.228.228.44:3827", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show help")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 DUEL LORDS Commands", color=0x7c4dff)
    embed.add_field(name="Commands", value="""
    `/register` - Register for tournament
    `/stats` - Show your statistics  
    `/ip` - Server information
    `/help` - This help message
    `/ping` - Bot latency
    """, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Latency: {latency}ms", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

# Run bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ No DISCORD_TOKEN found!")
        exit(1)
    
    print("🚀 Starting DUEL LORDS Bot...")
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Bot error: {e}")