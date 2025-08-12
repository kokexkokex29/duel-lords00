# BombSquad Tournament Bot

## Overview

The BombSquad Tournament Bot "Clan Lords |Bombsquad" is a comprehensive Discord bot designed to manage competitive gaming tournaments for the BombSquad game. The application provides tournament organization, player registration, match scheduling, and real-time competition management through Discord's slash command interface.

The bot enables players to register for tournaments, challenge each other to matches, view detailed statistics and leaderboards, and get BombSquad server connection information. Tournament organizers can create tournaments, manage brackets, and track match results through an intuitive command system. The application also features a web dashboard for monitoring bot activity and tournament statistics.

## Recent Updates (August 2025)

✅ **Complete Bot Implementation**: All 25+ Clan Lords |Bombsquad commands successfully implemented and operational
✅ **Discord Bot Fully Working**: Successfully connected to Discord Gateway with stable operation  
✅ **Guardian System**: Bot Runner with automatic restart protection implemented for 24/7 uptime
✅ **All Commands Operational**: register, stats, players, fighters, duel, record_result, matches, cancel_match, ip, help, about, ping, tournament, leaderboard, kill_stats, create_tournament, join_tournament, admin_match
✅ **Bot Name Updated**: Changed from "DUEL LORDS" to "Clan Lords |Bombsquad" throughout the system
✅ **Advanced Duel System**: Complete match scheduling with DM notifications and result recording
✅ **Enhanced Player Management**: Comprehensive statistics tracking, leaderboards, and rankings
✅ **JSON Database**: File-based storage for players, matches, and tournament data
✅ **Tournament Features**: Complete tournament management with rankings and statistics
✅ **Discord Token Security**: Properly configured with Replit Secrets for secure authentication
✅ **Command Sync Fixed**: Resolved duplicate command registration issues and restored all 25+ commands

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (August 2025)

- **2025-08-11**: Successfully fixed duplicate command registration issues
- **2025-08-11**: Restored all 25+ slash commands to full functionality
- **2025-08-11**: Prepared complete deployment package for render.com hosting
- **2025-08-11**: Created comprehensive deployment documentation and configuration files
- **2025-08-11**: Optimized bot performance and command synchronization
Bot persistence requirement: User wants the Discord bot to run continuously without stopping.
Bot reliability solution: Implemented Bot Guardian v2.0 with ultra-reliable monitoring every 15 seconds and automatic restart capability.
Project focus: Clan Lords |Bombsquad tournament bot system (not generic Discord bot dashboard)
Language support: English (primary), Portuguese (secondary) - Arabic support removed
Bot authentication: Discord token stored in DISCORD_TOKEN secret

## System Architecture

### Bot Architecture
The system follows a modular command-based architecture using Discord.py with slash commands. The main bot class (`BombSquadBot`) extends `commands.Bot` and loads command modules dynamically during startup. Commands are organized into separate cogs for different functionality areas: player management, tournament operations, match scheduling, and general utilities.

The bot uses Discord's modern interaction system for slash commands, providing a clean user interface within Discord. All commands are registered as application commands and automatically synced during bot startup. The modular design allows for easy maintenance and feature expansion.

### Data Storage
The application uses a file-based JSON database system for simplicity and portability. Three main data files store different entity types:
- `players.json` - Player registration data, statistics, win/loss records, and performance metrics
- `tournaments.json` - Tournament configurations, participant lists, brackets, and tournament state
- `matches.json` - Match scheduling, challenge system, results, and match history

The Database class provides an abstraction layer over file operations, handling JSON serialization/deserialization and ensuring data integrity. This approach was chosen for easy deployment without external database dependencies while maintaining data persistence.

### Scheduling System
Match scheduling is handled by an AsyncIOScheduler from the APScheduler library. The MatchScheduler class manages match reminders and notifications, running in the background alongside the bot. Scheduled jobs include match start reminders sent via direct messages to players 5 minutes before their scheduled match time.

The scheduler integrates with the bot's event loop and can dynamically add, remove, and modify scheduled tasks based on match creation, acceptance, and completion events.

### Web Server Integration
A Flask web server runs concurrently with the Discord bot using threading. The web component provides:
- Health check endpoints for monitoring and uptime tracking
- A status dashboard showing bot activity and tournament statistics
- Keep-alive functionality for cloud hosting platforms
- REST endpoints for external integrations

The web server enables monitoring of bot performance and provides a fallback interface for basic tournament information viewing.

### Command System Architecture
Commands are organized into logical groups with consistent error handling and response formatting. The system includes:
- Input validation and sanitization for all user commands
- Standardized embed responses for consistent user experience
- Permission-based command access (admin vs. regular users)
- Comprehensive error logging and user-friendly error messages

### Multilingual Support
The translation system supports multiple languages through a centralized translation dictionary. Currently implements English and Portuguese translations, with the infrastructure to easily add additional languages by extending the translation mappings.

## External Dependencies

### Discord API
- **discord.py** - Primary Discord bot framework for handling commands, events, and interactions with the Discord API
- **Discord Application** - Requires bot token and application registration for Discord integration

### Scheduling
- **APScheduler** - AsyncIO scheduler for managing timed events like match reminders and tournament automation

### Web Framework
- **Flask** - Lightweight web server for health checks, monitoring, and dashboard functionality
- **Werkzeug** - WSGI utilities and proxy fix middleware for proper request handling

### Hosting and Deployment
- **Threading** - Python threading module for concurrent execution of bot and web server
- **Environment Variables** - Configuration management for sensitive data like bot tokens and session keys
- **Keep-alive System** - Custom implementation for maintaining server uptime on cloud platforms
- **Render.com Deployment** - Complete configuration for production hosting with render.yaml, Procfile, and gunicorn setup
- **Requirements Management** - Dedicated requirements_render.txt for clean deployment dependencies

### Game Server Integration
- **BombSquad Server** - Integration with dedicated game server at IP `18.228.228.44:3827` for match hosting