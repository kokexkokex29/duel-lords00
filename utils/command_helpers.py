import discord
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CommandResponse:
    """Helper class for command responses"""
    
    @staticmethod
    def success(title, description, color=0x00ff00):
        """Create a success embed"""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.timestamp = datetime.now()
        return embed
    
    @staticmethod
    def error(title, description, color=0xff0000):
        """Create an error embed"""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.timestamp = datetime.now()
        return embed
    
    @staticmethod
    def info(title, description, color=0x0099ff):
        """Create an info embed"""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.timestamp = datetime.now()
        return embed

class CommandValidator:
    """Helper class for command validation"""
    
    @staticmethod
    def is_admin(interaction: discord.Interaction) -> bool:
        """Check if user has admin permissions"""
        if hasattr(interaction.user, 'guild_permissions'):
            return interaction.user.guild_permissions.administrator
        return False
    
    @staticmethod
    def validate_time_format(time_string: str) -> datetime:
        """Validate and parse time format"""
        try:
            return datetime.strptime(time_string, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Invalid time format. Use YYYY-MM-DD HH:MM")
    
    @staticmethod
    def validate_user_registered(db, user_id: str) -> bool:
        """Check if user is registered"""
        return db.get_player(user_id) is not None

class EmbedBuilder:
    """Helper class for building embeds"""
    
    def __init__(self, title="", description="", color=discord.Color.blue()):
        self.embed = discord.Embed(title=title, description=description, color=color)
        self.embed.timestamp = datetime.now()
    
    def add_field(self, name, value, inline=False):
        """Add field to embed"""
        self.embed.add_field(name=name, value=value, inline=inline)
        return self
    
    def set_footer(self, text, icon_url=None):
        """Set embed footer"""
        self.embed.set_footer(text=text, icon_url=icon_url)
        return self
    
    def set_thumbnail(self, url):
        """Set embed thumbnail"""
        self.embed.set_thumbnail(url=url)
        return self
    
    def build(self):
        """Build and return the embed"""
        return self.embed

class MatchManager:
    """Helper class for match management"""
    
    def __init__(self, db):
        self.db = db
    
    def create_match(self, challenger_id, opponent_id, scheduled_time, description):
        """Create a new match"""
        return self.db.create_match(challenger_id, opponent_id, scheduled_time, description)
    
    def accept_match(self, match_id, user_id):
        """Accept a match challenge"""
        match = self.db.get_match(match_id)
        if not match:
            raise ValueError("Match not found")
        
        if match['opponent_id'] != user_id:
            raise ValueError("Not your challenge to accept")
        
        if match['status'] != 'pending':
            raise ValueError("Match already responded to")
        
        match['status'] = 'accepted'
        self.db.update_match(match_id, match)
        return match
    
    def decline_match(self, match_id, user_id):
        """Decline a match challenge"""
        match = self.db.get_match(match_id)
        if not match:
            raise ValueError("Match not found")
        
        if match['opponent_id'] != user_id:
            raise ValueError("Not your challenge to decline")
        
        if match['status'] != 'pending':
            raise ValueError("Match already responded to")
        
        match['status'] = 'declined'
        self.db.update_match(match_id, match)
        return match
    
    def complete_match(self, match_id, winner_id, stats=None):
        """Complete a match with results"""
        match = self.db.get_match(match_id)
        if not match:
            raise ValueError("Match not found")
        
        if match['status'] != 'accepted':
            raise ValueError("Match not accepted")
        
        challenger_id = match['challenger_id']
        opponent_id = match['opponent_id']
        
        if winner_id not in [challenger_id, opponent_id]:
            raise ValueError("Invalid winner")
        
        match['status'] = 'completed'
        match['winner_id'] = winner_id
        match['completed_at'] = datetime.now().isoformat()
        
        if stats:
            match['stats'] = stats
        
        self.db.update_match(match_id, match)
        
        # Update player statistics
        self._update_player_stats(challenger_id, opponent_id, winner_id, stats)
        
        return match
    
    def _update_player_stats(self, challenger_id, opponent_id, winner_id, stats):
        """Update player statistics after match"""
        challenger_data = self.db.get_player(challenger_id)
        opponent_data = self.db.get_player(opponent_id)
        
        if not challenger_data or not opponent_data:
            return
        
        # Update win/loss records
        if winner_id == challenger_id:
            challenger_data['wins'] += 1
            opponent_data['losses'] += 1
        else:
            challenger_data['losses'] += 1
            opponent_data['wins'] += 1
        
        # Update kill/death stats if provided
        if stats:
            challenger_data['kills'] += stats.get('challenger_kills', 0)
            challenger_data['deaths'] += stats.get('challenger_deaths', 0)
            opponent_data['kills'] += stats.get('opponent_kills', 0)
            opponent_data['deaths'] += stats.get('opponent_deaths', 0)
        
        self.db.update_player(challenger_id, challenger_data)
        self.db.update_player(opponent_id, opponent_data)
