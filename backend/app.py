from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from models import Team, Game, Bracket, BracketMatch, TournamentSettings
from datetime import datetime

def create_app():
    app = Flask(__name__)
    # Configure CORS with explicit headers and handle all URL patterns
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
             "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "expose_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin", 
                             "Access-Control-Allow-Methods", "Access-Control-Allow-Headers"]
         }},
         supports_credentials=False)
    
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tournament.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

# Add a before_request handler to ensure proper CORS headers on all responses
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
        return response

# Basic route
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Tournament App API!"})

# Team routes
@app.route('/api/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    return jsonify([team.to_dict() for team in teams])

@app.route('/teams', methods=['GET'])
def get_teams_alt():
    # Alternative endpoint for compatibility
    teams = Team.query.all()
    return jsonify([team.to_dict() for team in teams])

@app.route('/api/teams', methods=['POST'])
def add_team():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check if name is present
        if 'name' not in data:
            return jsonify({"error": "Team name is required"}), 400
            
        new_team = Team(
            name=data['name'],
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            runs_scored=data.get('runs_scored', 0),
            runs_allowed=data.get('runs_allowed', 0),
            run_differential=data.get('run_differential', 0),
            games_played=data.get('games_played', 0)
        )
        db.session.add(new_team)
        db.session.commit()
        return jsonify(new_team.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/teams', methods=['POST'])
def add_team_alt():
    # Alternative endpoint for compatibility
    return add_team()

@app.route('/api/teams/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    try:
        team = Team.query.get_or_404(team_id)
        db.session.delete(team)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/teams/<int:team_id>', methods=['DELETE'])
def delete_team_alt(team_id):
    # Alternative endpoint for compatibility
    return delete_team(team_id)

# Rankings endpoint
@app.route('/rankings', methods=['GET'])
def get_rankings():
    try:
        # Fetch all teams
        teams = Team.query.all()
        
        # Calculate winning percentage for each team
        for team in teams:
            if team.games_played > 0:
                team.win_percentage = round(team.wins / team.games_played, 3)
            else:
                team.win_percentage = 0.0
        
        # Sort teams: 
        # 1. By wins (descending)
        # 2. By runs allowed (ascending - fewer runs against is better)
        ranked_teams = sorted(
            teams, 
            key=lambda t: (
                -(t.wins or 0),  # Negative for descending order
                t.runs_allowed or 0  # Ascending order (fewer runs allowed is better)
            )
        )
        
        # Create rankings with rank attribute
        rankings_data = []
        for index, team in enumerate(ranked_teams):
            team_data = team.to_dict()
            team_data['rank'] = index + 1  # Add rank (1-based)
            
            # Add win percentage to the response
            if team.games_played > 0:
                team_data['win_percentage'] = round(team.wins / team.games_played, 3)
            else:
                team_data['win_percentage'] = 0.0
                
            rankings_data.append(team_data)
        
        return jsonify(rankings_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bracket endpoint
@app.route('/bracket', methods=['GET'])
def get_bracket():
    try:
        # Get all bracket matches organized by rounds
        matches = BracketMatch.query.order_by(BracketMatch.round_number, BracketMatch.match_display_id).all()
        
        # If no matches exist, return empty structure
        if not matches:
            return jsonify({"rounds": {}})
        
        # Organize matches by round
        rounds = {}
        for match in matches:
            round_num = str(match.round_number)
            if round_num not in rounds:
                rounds[round_num] = []
            
            # Get team data if teams exist
            team1 = Team.query.get(match.team1_id) if match.team1_id else None
            team2 = Team.query.get(match.team2_id) if match.team2_id else None
            winner = Team.query.get(match.winner_id) if match.winner_id else None
            
            match_data = {
                'matchId': match.match_display_id,
                'round': match.round_number,
                'team1': team1.to_dict() if team1 else None,
                'team2': team2.to_dict() if team2 else None,
                'team1_score': match.team1_score,
                'team2_score': match.team2_score,
                'winner': winner.to_dict() if winner else None,
                'status': match.status
            }
            rounds[round_num].append(match_data)
        
        return jsonify({"rounds": rounds})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bracket/generate', methods=['POST'])
def generate_bracket():
    """Generate a new tournament bracket"""
    try:
        # Clear existing bracket data
        BracketMatch.query.delete()
        db.session.commit()
        
        # Fetch teams ranked by win percentage
        teams = Team.query.all()
        
        # Calculate winning percentage for each team
        for team in teams:
            if team.games_played > 0:
                team.win_percentage = round(team.wins / team.games_played, 3)
            else:
                team.win_percentage = 0.0
                
        # Sort teams by win percentage (descending)
        seeded_teams = sorted(
            teams, 
            key=lambda t: (
                t.win_percentage or 0,
                t.wins or 0, 
                t.run_differential or 0,
                t.runs_scored or 0
            ), 
            reverse=True
        )
        
        # Check if we have enough teams
        if len(seeded_teams) < 2:
            return jsonify({"error": "Not enough teams to create a bracket. Add at least 2 teams."}), 400
            
        # Determine number of rounds needed based on team count
        team_count = len(seeded_teams)
        total_slots = 1
        round_count = 0
        
        while total_slots < team_count:
            total_slots *= 2
            round_count += 1
            
        # If we need more teams to fill bracket, add byes
        while len(seeded_teams) < total_slots:
            seeded_teams.append(None)
            
        # Create first round matches
        match_id = 1
        first_round_matches = []
        
        for i in range(0, len(seeded_teams), 2):
            team1 = seeded_teams[i]
            team2 = seeded_teams[i+1] if i+1 < len(seeded_teams) else None
            
            # Determine match status
            if team1 is None or team2 is None:
                status = 'Bye'
                winner_id = team1.id if team1 else (team2.id if team2 else None)
            else:
                status = 'Scheduled'
                winner_id = None
                
            match = BracketMatch(
                match_display_id=match_id,
                round_number=1,
                team1_id=team1.id if team1 else None,
                team2_id=team2.id if team2 else None,
                team1_score=None,
                team2_score=None,
                winner_id=winner_id,
                status=status
            )
            
            db.session.add(match)
            first_round_matches.append(match)
            match_id += 1
            
        # Create subsequent rounds with empty matches
        for round_num in range(2, round_count + 1):
            matches_in_round = total_slots // (2 ** round_num)
            
            for i in range(matches_in_round):
                match = BracketMatch(
                    match_display_id=match_id,
                    round_number=round_num,
                    team1_id=None,
                    team2_id=None,
                    team1_score=None,
                    team2_score=None,
                    winner_id=None,
                    status='Pending'
                )
                
                db.session.add(match)
                match_id += 1
                
        db.session.commit()
        
        # Return the generated bracket
        return get_bracket()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/bracket/clear', methods=['POST'])
def clear_bracket():
    """Clear the tournament bracket without generating a new one"""
    try:
        # Delete all bracket matches
        BracketMatch.query.delete()
        db.session.commit()
        return jsonify({"message": "Tournament bracket cleared successfully", "rounds": {}})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/bracket/match/<int:match_id>', methods=['PATCH'])
def update_bracket_match(match_id):
    """Update a bracket match score and advance winner"""
    try:
        data = request.get_json()
        
        # Find the match
        match = BracketMatch.query.filter_by(match_display_id=match_id).first()
        if not match:
            return jsonify({"error": f"Match ID {match_id} not found"}), 404
            
        # Check if match is in a state that can be updated
        if match.status not in ['Scheduled']:
            return jsonify({"error": f"Cannot update match in {match.status} status"}), 400
            
        # Validate inputs
        if 'team1_score' not in data or 'team2_score' not in data:
            return jsonify({"error": "Missing required fields: team1_score, team2_score"}), 400
            
        team1_score = data['team1_score']
        team2_score = data['team2_score']
        
        if team1_score < 0 or team2_score < 0:
            return jsonify({"error": "Scores cannot be negative"}), 400
            
        # Update the match scores
        match.team1_score = team1_score
        match.team2_score = team2_score
        match.status = 'Complete'
        
        # Determine the winner
        if team1_score > team2_score:
            match.winner_id = match.team1_id
        elif team2_score > team1_score:
            match.winner_id = match.team2_id
        else:
            return jsonify({"error": "There must be a winner in bracket play"}), 400
            
        # Advance the winner to the next round
        next_round = match.round_number + 1
        
        # Calculate which match in the next round this feeds into
        next_match_index = (match.match_display_id - (2**(match.round_number-1))) // 2 + 1
        next_match_position = (match.match_display_id - (2**(match.round_number-1))) % 2
        
        # Find the next round match
        next_match = BracketMatch.query.filter_by(
            round_number=next_round,
            match_display_id=next_match_index + (2**(next_round-1) - 1)
        ).first()
        
        # If there is a next match, advance the winner
        if next_match:
            if next_match_position == 0:  # Team 1 position
                next_match.team1_id = match.winner_id
            else:  # Team 2 position
                next_match.team2_id = match.winner_id
                
            # If both teams are assigned, update status
            if next_match.team1_id is not None and next_match.team2_id is not None:
                next_match.status = 'Scheduled'
        
        db.session.commit()
        return jsonify({"message": "Match updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- Game Endpoints ---

@app.route('/games', methods=['POST', 'OPTIONS'])
@app.route('/games/', methods=['POST', 'OPTIONS'])
def add_game_score():
    # Handle OPTIONS requests explicitly
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-Requested-With'
        return response
        
    data = request.get_json()
    required_fields = ['team1_id', 'team2_id', 'team1_score', 'team2_score']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: team1_id, team2_id, team1_score, team2_score'}), 400

    try:
        team1_id = int(data['team1_id'])
        team2_id = int(data['team2_id'])
        team1_score = int(data['team1_score'])
        team2_score = int(data['team2_score'])
    except ValueError:
        return jsonify({'error': 'Team IDs and scores must be integers'}), 400

    if team1_id == team2_id:
        return jsonify({'error': 'A team cannot play against itself'}), 400

    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)

    if not team1 or not team2:
        return jsonify({'error': 'One or both teams not found'}), 404

    # Update team stats (simplified example - adjust logic as needed)
    team1.games_played += 1
    team2.games_played += 1
    team1.runs_scored += team1_score
    team1.runs_allowed += team2_score
    team2.runs_scored += team2_score
    team2.runs_allowed += team1_score

    if team1_score > team2_score:
        team1.wins += 1
        team2.losses += 1
    elif team2_score > team1_score:
        team2.wins += 1
        team1.losses += 1

    team1.run_differential = team1.runs_scored - team1.runs_allowed
    team2.run_differential = team2.runs_scored - team2.runs_allowed

    try:
        # Note: We are not creating a Game record here, just updating teams.
        # If you need to store game records, add the Game model creation here.
        db.session.commit()
        return jsonify({'message': 'Game score processed and team stats updated successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- Schedule Management Endpoints ---

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get all scheduled games"""
    try:
        games = Game.query.order_by(Game.date, Game.time).all()
        return jsonify([game.to_dict() for game in games])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Get a specific game by ID"""
    try:
        game = Game.query.get_or_404(game_id)
        return jsonify(game.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule', methods=['POST'])
def create_game():
    """Create a new scheduled game"""
    try:
        data = request.get_json()
        required_fields = ['team1_id', 'team2_id', 'date', 'time', 'field']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        # Parse date and time
        try:
            game_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            game_time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time'}), 400
        
        # Validate team IDs
        team1_id = int(data['team1_id'])
        team2_id = int(data['team2_id'])
        
        if team1_id == team2_id:
            return jsonify({'error': 'A team cannot play against itself'}), 400
            
        team1 = Team.query.get(team1_id)
        team2 = Team.query.get(team2_id)
        
        if not team1 or not team2:
            return jsonify({'error': 'One or both teams not found'}), 404
        
        # Create new game
        new_game = Game(
            team1_id=team1_id,
            team2_id=team2_id,
            date=game_date,
            time=game_time,
            field=data['field'],
            team1_score=data.get('team1_score'),
            team2_score=data.get('team2_score'),
            status=data.get('status', 'Scheduled')
        )
        
        db.session.add(new_game)
        db.session.commit()
        
        return jsonify(new_game.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    """Update a scheduled game"""
    try:
        game = Game.query.get_or_404(game_id)
        data = request.get_json()
        
        if 'team1_id' in data:
            game.team1_id = int(data['team1_id'])
            
        if 'team2_id' in data:
            game.team2_id = int(data['team2_id'])
            
        if 'date' in data:
            game.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            
        if 'time' in data:
            game.time = datetime.strptime(data['time'], '%H:%M').time()
            
        if 'field' in data:
            game.field = data['field']
            
        if 'team1_score' in data:
            game.team1_score = data['team1_score']
            
        if 'team2_score' in data:
            game.team2_score = data['team2_score']
            
        if 'status' in data:
            game.status = data['status']
        
        db.session.commit()
        return jsonify(game.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    """Delete a scheduled game"""
    try:
        game = Game.query.get_or_404(game_id)
        db.session.delete(game)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/<int:game_id>/score', methods=['PUT', 'OPTIONS'])
def update_game_score(game_id):
    """Update the score for a game"""
    # Handle OPTIONS requests explicitly
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-Requested-With'
        return response
        
    try:
        game = Game.query.get_or_404(game_id)
        data = request.get_json()
        
        if not data or not all(field in data for field in ['team1_score', 'team2_score']):
            return jsonify({'error': 'Missing required fields: team1_score, team2_score'}), 400
        
        team1 = Team.query.get(game.team1_id)
        team2 = Team.query.get(game.team2_id)
        
        if not team1 or not team2:
            return jsonify({'error': 'One or both teams not found'}), 404
            
        # First, handle the case where the game already has scores
        # We need to reverse the previous score's effect on team stats
        if game.team1_score is not None and game.team2_score is not None and game.status == 'Completed':
            # Subtract previous scores from team stats
            team1.runs_scored -= game.team1_score
            team1.runs_allowed -= game.team2_score
            team2.runs_scored -= game.team2_score
            team2.runs_allowed -= game.team1_score
            
            # Reverse win/loss records
            if game.team1_score > game.team2_score:
                team1.wins -= 1
                team2.losses -= 1
            elif game.team2_score > game.team1_score:
                team2.wins -= 1
                team1.losses -= 1
                
            # Also decrement games_played if this is the first time the game is being completed
            if game.status != 'Completed':
                team1.games_played -= 1
                team2.games_played -= 1
        
        # Update game scores
        game.team1_score = data['team1_score']
        game.team2_score = data['team2_score']
        
        # Also update status if provided
        old_status = game.status
        if 'status' in data:
            game.status = data['status']
        else:
            # If status not provided, set to Completed when scores are updated
            game.status = 'Completed'
            
        # Now update team stats with new scores
        if game.status == 'Completed':
            # If this is a newly completed game, increment games_played
            if old_status != 'Completed':
                team1.games_played += 1
                team2.games_played += 1
                
            # Add new scores to team stats
            team1.runs_scored += game.team1_score
            team1.runs_allowed += game.team2_score
            team2.runs_scored += game.team2_score
            team2.runs_allowed += game.team1_score
            
            # Update win/loss records
            if game.team1_score > game.team2_score:
                team1.wins += 1
                team2.losses += 1
            elif game.team2_score > game.team1_score:
                team2.wins += 1
                team1.losses += 1
                
            # Update run differentials
            team1.run_differential = team1.runs_scored - team1.runs_allowed
            team2.run_differential = team2.runs_scored - team2.runs_allowed
            
        db.session.commit()
        return jsonify(game.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- Tournament Settings Endpoints ---

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get tournament settings"""
    try:
        # Get the first settings object or create one if it doesn't exist
        settings = TournamentSettings.query.first()
        if not settings:
            settings = TournamentSettings(name="Baseball Tournament")
            db.session.add(settings)
            db.session.commit()
        
        return jsonify(settings.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update tournament settings"""
    try:
        data = request.get_json()
        
        # Get the first settings object or create one if it doesn't exist
        settings = TournamentSettings.query.first()
        if not settings:
            settings = TournamentSettings()
            db.session.add(settings)
        
        # Update fields if they exist in the request
        if 'name' in data:
            settings.name = data['name']
        
        if 'description' in data:
            settings.description = data['description']
        
        db.session.commit()
        return jsonify(settings.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
