import json
import os
from flask import render_template, jsonify, request
from app import app
from database import Database
import logging

logger = logging.getLogger(__name__)

# Initialize database
db = Database()

@app.route('/')
def index():
    """Home page"""
    try:
        # Get basic statistics
        players = db.get_all_players()
        tournaments = db.get_all_tournaments()
        matches = db.get_all_matches()
        
        stats = {
            'total_players': len(players),
            'total_tournaments': len(tournaments),
            'total_matches': len(matches),
            'active_tournaments': len([t for t in tournaments.values() if t['status'] == 'active'])
        }
        
        return render_template('index.html', stats=stats)
        
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return render_template('index.html', stats={})

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    try:
        # Get all data for dashboard
        players = db.get_all_players()
        tournaments = db.get_all_tournaments()
        matches = db.get_all_matches()
        
        # Calculate statistics
        stats = {
            'total_players': len(players),
            'total_tournaments': len(tournaments),
            'total_matches': len(matches),
            'active_tournaments': len([t for t in tournaments.values() if t['status'] == 'active']),
            'completed_matches': len([m for m in matches.values() if m['status'] == 'completed']),
            'pending_matches': len([m for m in matches.values() if m['status'] == 'pending'])
        }
        
        # Top players by wins
        top_players = sorted(
            players.values(), 
            key=lambda p: p['wins'], 
            reverse=True
        )[:10]
        
        # Recent matches
        recent_matches = sorted(
            matches.values(),
            key=lambda m: m['created_at'],
            reverse=True
        )[:10]
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             top_players=top_players,
                             recent_matches=recent_matches)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', stats={}, top_players=[], recent_matches=[])

@app.route('/bot-status')
def bot_status():
    """Bot management and status page"""
    try:
        # Check bot status
        bot_token_exists = bool(os.environ.get('DISCORD_TOKEN'))
        
        # Get bot statistics
        stats = {
            'token_configured': bot_token_exists,
            'bot_online': False,  # We'll update this when bot is connected
            'total_commands': 25,  # Number of available commands
            'server_ip': '18.228.228.44:3827'
        }
        
        # Get recent bot activity logs
        activity_logs = [
            {'time': '2025-01-11 15:50:02', 'action': 'Bot started', 'status': 'success'},
            {'time': '2025-01-11 15:49:41', 'action': 'Commands synced', 'status': 'success'},
            {'time': '2025-01-11 15:48:33', 'action': 'Database connected', 'status': 'success'}
        ]
        
        return render_template('bot_status.html', stats=stats, activity_logs=activity_logs)
        
    except Exception as e:
        logger.error(f"Error loading bot status: {e}")
        return render_template('bot_status.html', stats={}, activity_logs=[])

@app.route('/players')
def players():
    """Players page"""
    try:
        players = db.get_all_players()
        
        # Sort players by wins
        sorted_players = sorted(
            players.values(),
            key=lambda p: (p['wins'], p['kills'] / max(p['deaths'], 1)),
            reverse=True
        )
        
        return render_template('players.html', players=sorted_players)
        
    except Exception as e:
        logger.error(f"Error loading players: {e}")
        return render_template('players.html', players=[])

@app.route('/matches')
def matches():
    """Matches page"""
    try:
        matches = db.get_all_matches()
        players = db.get_all_players()
        
        # Sort matches by creation date
        sorted_matches = sorted(
            matches.values(),
            key=lambda m: m['created_at'],
            reverse=True
        )
        
        return render_template('matches.html', matches=sorted_matches, players=players)
        
    except Exception as e:
        logger.error(f"Error loading matches: {e}")
        return render_template('matches.html', matches=[], players={})

@app.route('/tournaments')
def tournaments():
    """Tournaments page"""
    try:
        tournaments = db.get_all_tournaments()
        
        # Sort tournaments by creation date
        sorted_tournaments = sorted(
            tournaments.values(),
            key=lambda t: t['created_at'],
            reverse=True
        )
        
        return render_template('tournaments.html', tournaments=sorted_tournaments)
        
    except Exception as e:
        logger.error(f"Error loading tournaments: {e}")
        return render_template('tournaments.html', tournaments=[])

@app.route('/api/stats')
def api_stats():
    """API endpoint for live statistics"""
    try:
        players = db.get_all_players()
        tournaments = db.get_all_tournaments()
        matches = db.get_all_matches()
        
        stats = {
            'total_players': len(players),
            'total_tournaments': len(tournaments),
            'total_matches': len(matches),
            'active_tournaments': len([t for t in tournaments.values() if t['status'] == 'active']),
            'completed_matches': len([m for m in matches.values() if m['status'] == 'completed']),
            'pending_matches': len([m for m in matches.values() if m['status'] == 'pending'])
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@app.route('/api/players')
def api_players():
    """API endpoint for players data"""
    try:
        players = db.get_all_players()
        return jsonify(list(players.values()))
        
    except Exception as e:
        logger.error(f"Error getting API players: {e}")
        return jsonify({'error': 'Failed to get players'}), 500

@app.route('/keep-alive')
def keep_alive_endpoint():
    """Keep alive endpoint for hosting services"""
    return jsonify({
        'status': 'alive',
        'message': 'BombSquad Tournament Bot is running',
        'timestamp': db.get_current_timestamp()
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {error}")
    return render_template('base.html'), 500
