import json
import os
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
        
        # File paths
        self.players_file = os.path.join(self.data_dir, "players.json")
        self.matches_file = os.path.join(self.data_dir, "matches.json")
        self.tournaments_file = os.path.join(self.data_dir, "tournaments.json")
        
        # Initialize files if they don't exist
        self.init_files()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def init_files(self):
        """Initialize JSON files if they don't exist"""
        for file_path in [self.players_file, self.matches_file, self.tournaments_file]:
            if not os.path.exists(file_path):
                self.save_json(file_path, {})
    
    def load_json(self, file_path):
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_json(self, file_path, data):
        """Save JSON data to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving to {file_path}: {e}")
    
    def get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    def generate_id(self):
        """Generate a unique ID"""
        return str(uuid.uuid4())[:8]
    
    # Player methods
    def register_player(self, user_id, name):
        """Register a new player"""
        players = self.load_json(self.players_file)
        
        if user_id in players:
            return False
        
        player_data = {
            'user_id': user_id,
            'name': name,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'kills': 0,
            'deaths': 0,
            'registered_at': self.get_current_timestamp(),
            'last_updated': self.get_current_timestamp()
        }
        
        players[user_id] = player_data
        self.save_json(self.players_file, players)
        return True
    
    def get_player(self, user_id):
        """Get player data"""
        players = self.load_json(self.players_file)
        return players.get(user_id)
    
    def get_all_players(self):
        """Get all players"""
        return self.load_json(self.players_file)
    
    def update_player_stats(self, user_id, wins=0, losses=0, draws=0, kills=0, deaths=0):
        """Update player statistics"""
        players = self.load_json(self.players_file)
        
        if str(user_id) not in players:
            return False
        
        player = players[str(user_id)]
        player['wins'] += wins
        player['losses'] += losses
        player['draws'] += draws
        player['kills'] += kills
        player['deaths'] += deaths
        player['last_updated'] = self.get_current_timestamp()
        
        self.save_json(self.players_file, players)
        return True
    
    # Match methods
    def create_match(self, challenger_id, opponent_id, scheduled_time, description="Duel Match"):
        """Create a new match"""
        matches = self.load_json(self.matches_file)
        match_id = self.generate_id()
        
        match_data = {
            'id': match_id,
            'player1_id': challenger_id,
            'player2_id': opponent_id,
            'scheduled_time': scheduled_time,
            'description': description,
            'status': 'scheduled',
            'created_at': self.get_current_timestamp(),
            'completed_at': None,
            'winner_id': None,
            'reminder_sent': False,
            'result': None
        }
        
        matches[match_id] = match_data
        self.save_json(self.matches_file, matches)
        return match_id
    
    def get_upcoming_matches(self):
        """Get all upcoming scheduled matches"""
        matches = self.load_json(self.matches_file)
        upcoming = []
        
        for match_id, match_data in matches.items():
            if match_data.get('status') == 'scheduled':
                match_data['id'] = match_id
                upcoming.append(match_data)
        
        # Sort by scheduled time
        upcoming.sort(key=lambda x: x['scheduled_time'])
        return upcoming
    
    def update_match_reminder_status(self, match_id, sent):
        """Update reminder sent status for a match"""
        matches = self.load_json(self.matches_file)
        
        if match_id in matches:
            matches[match_id]['reminder_sent'] = sent
            self.save_json(self.matches_file, matches)
            return True
        return False
    
    def update_match_status(self, match_id, status):
        """Update match status"""
        matches = self.load_json(self.matches_file)
        
        if match_id in matches:
            matches[match_id]['status'] = status
            matches[match_id]['last_updated'] = self.get_current_timestamp()
            self.save_json(self.matches_file, matches)
            return True
        return False
    
    def record_match_result(self, match_id, result_data):
        """Record the result of a completed match"""
        matches = self.load_json(self.matches_file)
        
        if match_id in matches:
            matches[match_id]['result'] = result_data
            matches[match_id]['status'] = 'completed'
            matches[match_id]['completed_at'] = self.get_current_timestamp()
            matches[match_id]['winner_id'] = result_data.get('winner_id')
            self.save_json(self.matches_file, matches)
            return True
        return False
    
    def cancel_match(self, match_id):
        """Cancel a scheduled match"""
        matches = self.load_json(self.matches_file)
        
        if match_id in matches:
            matches[match_id]['status'] = 'cancelled'
            matches[match_id]['cancelled_at'] = self.get_current_timestamp()
            self.save_json(self.matches_file, matches)
            return True
        return False
    
    def get_match(self, match_id):
        """Get match by ID"""
        matches = self.load_json(self.matches_file)
        return matches.get(match_id)
    
    def update_match(self, match_id, match_data):
        """Update match data"""
        matches = self.load_json(self.matches_file)
        matches[match_id] = match_data
        self.save_json(self.matches_file, matches)
        return match_data
    
    def get_all_matches(self):
        """Get all matches"""
        return self.load_json(self.matches_file)
    
    # Tournament methods
    def create_tournament(self, name, description, max_players, creator_id):
        """Create a new tournament"""
        tournaments = self.load_json(self.tournaments_file)
        tournament_id = self.generate_id()
        
        tournament_data = {
            'id': tournament_id,
            'name': name,
            'description': description,
            'max_players': max_players,
            'creator_id': creator_id,
            'participants': [],
            'status': 'registration',
            'created_at': self.get_current_timestamp(),
            'started_at': None,
            'completed_at': None,
            'matches': []
        }
        
        tournaments[tournament_id] = tournament_data
        self.save_json(self.tournaments_file, tournaments)
        return tournament_id
    
    def get_tournament(self, tournament_id):
        """Get tournament by ID"""
        tournaments = self.load_json(self.tournaments_file)
        return tournaments.get(tournament_id)
    
    def update_tournament(self, tournament_id, tournament_data):
        """Update tournament data"""
        tournaments = self.load_json(self.tournaments_file)
        tournaments[tournament_id] = tournament_data
        self.save_json(self.tournaments_file, tournaments)
        return tournament_data
    
    def get_all_tournaments(self):
        """Get all tournaments"""
        return self.load_json(self.tournaments_file)
