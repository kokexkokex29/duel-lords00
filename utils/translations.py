# Translation system for multi-language support (English + Portuguese)
TRANSLATIONS = {
    'en': {
        # Player messages
        'player.already_registered': '✅ You are already registered for tournaments!',
        'player.must_register': '❌ You must register first using `/register`.',
        'player.not_registered': '❌ This player is not registered.',
        'player.opponent_not_registered': '❌ The opponent is not registered.',
        'player.no_players': '❌ No players registered yet.',
        'player.registered_success': '✅ Successfully registered! Welcome to Duel Lords tournaments.',
        'player.profile_updated': '✅ Profile updated successfully!',
        
        # Match messages
        'match.cannot_challenge_self': '❌ You cannot challenge yourself!',
        'match.invalid_time_format': '❌ Invalid time format. Use YYYY-MM-DD HH:MM',
        'match.not_found': '❌ Match not found.',
        'match.not_your_challenge': '❌ This is not your challenge to respond to.',
        'match.already_responded': '❌ This challenge has already been responded to.',
        'match.not_accepted': '❌ This match has not been accepted yet.',
        'match.invalid_winner': '❌ Invalid winner specified.',
        'match.challenge_sent': '⚔️ Challenge sent successfully!',
        'match.challenge_accepted': '✅ Challenge accepted! Match scheduled.',
        'match.challenge_declined': '❌ Challenge declined.',
        'match.result_recorded': '🏆 Match result recorded successfully!',
        
        # Tournament messages
        'tournament.not_found': '❌ Tournament not found.',
        'tournament.registration_closed': '❌ Tournament registration is closed.',
        'tournament.full': '❌ This tournament is full.',
        'tournament.already_joined': '❌ You are already in this tournament.',
        'tournament.already_started': '❌ This tournament has already started.',
        'tournament.not_enough_players': '❌ At least 2 players are required to start.',
        'tournament.created': '🏆 Tournament created successfully!',
        'tournament.joined': '✅ Successfully joined tournament!',
        'tournament.started': '🎮 Tournament has started!',
        
        # Server info
        'server.title': '🎮 BombSquad Tournament Server',
        'server.status_online': '🟢 Online',
        'server.status_offline': '🔴 Offline',
        'server.players_online': 'Players Online',
        'server.max_players': 'Max Players',
        
        # General messages
        'errors.general': '❌ An error occurred. Please try again.',
        'errors.missing_permissions': '❌ You do not have permission to use this command.',
        'success.general': '✅ Operation completed successfully!',
    },
    'pt': {
        # Player messages
        'player.already_registered': '✅ Você já está registrado para torneios!',
        'player.must_register': '❌ Você deve se registrar primeiro usando `/register`.',
        'player.not_registered': '❌ Este jogador não está registrado.',
        'player.opponent_not_registered': '❌ O oponente não está registrado.',
        'player.no_players': '❌ Nenhum jogador registrado ainda.',
        'player.registered_success': '✅ Registrado com sucesso! Bem-vindo aos torneios Duel Lords.',
        'player.profile_updated': '✅ Perfil atualizado com sucesso!',
        
        # Match messages
        'match.cannot_challenge_self': '❌ Você não pode desafiar a si mesmo!',
        'match.invalid_time_format': '❌ Formato de hora inválido. Use AAAA-MM-DD HH:MM',
        'match.not_found': '❌ Partida não encontrada.',
        'match.not_your_challenge': '❌ Este não é seu desafio para responder.',
        'match.already_responded': '❌ Este desafio já foi respondido.',
        'match.not_accepted': '❌ Esta partida ainda não foi aceita.',
        'match.invalid_winner': '❌ Vencedor inválido especificado.',
        'match.challenge_sent': '⚔️ Desafio enviado com sucesso!',
        'match.challenge_accepted': '✅ Desafio aceito! Partida agendada.',
        'match.challenge_declined': '❌ Desafio recusado.',
        'match.result_recorded': '🏆 Resultado da partida registrado com sucesso!',
        
        # Tournament messages
        'tournament.not_found': '❌ Torneio não encontrado.',
        'tournament.registration_closed': '❌ As inscrições do torneio estão fechadas.',
        'tournament.full': '❌ Este torneio está lotado.',
        'tournament.already_joined': '❌ Você já está neste torneio.',
        'tournament.already_started': '❌ Este torneio já começou.',
        'tournament.not_enough_players': '❌ Pelo menos 2 jogadores são necessários para começar.',
        'tournament.created': '🏆 Torneio criado com sucesso!',
        'tournament.joined': '✅ Juntou-se ao torneio com sucesso!',
        'tournament.started': '🎮 O torneio começou!',
        
        # Server info
        'server.title': '🎮 Servidor de Torneio BombSquad',
        'server.status_online': '🟢 Online',
        'server.status_offline': '🔴 Offline',
        'server.players_online': 'Jogadores Online',
        'server.max_players': 'Máx. Jogadores',
        
        # General messages
        'errors.general': '❌ Ocorreu um erro. Tente novamente.',
        'errors.missing_permissions': '❌ Você não tem permissão para usar este comando.',
        'success.general': '✅ Operação concluída com sucesso!',
    }
}

def get_translation(key, language='en'):
    """Get translation for a key in specified language"""
    return TRANSLATIONS.get(language, TRANSLATIONS['en']).get(key, key)

def get_text(key, language='en'):
    """Alias for get_translation"""
    return get_translation(key, language)
