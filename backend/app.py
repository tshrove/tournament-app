from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from models import Team, Game, BracketMatch, TournamentSettings, Tournament, TournamentBracketStorage
from datetime import datetime
import json

def create_app():
    app = Flask(__name__)
    # Configure CORS with explicit headers and handle all URL patterns
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:8080", "http://localhost", 
                         "http://localhost:80", "http://127.0.0.1:8080", 
                        "http://ec2-44-194-164-99.compute-1.amazonaws.com",
                        "http://ec2-44-194-164-99.compute-1.amazonaws.com:80"],
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
    return jsonify({"message": "Welcome to the Rocketpad API!"})

# Team routes
@app.route('/api/teams', methods=['GET'])
def get_teams():
    tournament_id = request.args.get('tournament_id')
    query = Team.query
    
    if tournament_id:
        query = query.filter_by(tournament_id=tournament_id)
    
    teams = query.all()
    return jsonify([team.to_dict() for team in teams])

@app.route('/teams', methods=['GET'])
def get_teams_alt():
    # Alternative endpoint for compatibility
    tournament_id = request.args.get('tournament_id')
    query = Team.query
    
    if tournament_id:
        query = query.filter_by(tournament_id=tournament_id)
    
    teams = query.all()
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
            games_played=data.get('games_played', 0),
            tournament_id=data.get('tournament_id')
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
        tournament_id = request.args.get('tournament_id')
        
        # Fetch teams with optional tournament filter
        query = Team.query
        if tournament_id:
            query = query.filter_by(tournament_id=tournament_id)
            
        teams = query.all()
        
        # Calculate winning percentage for each team
        for team in teams:
            if team.games_played > 0:
                team.win_percentage = round(team.wins / team.games_played, 3)
            else:
                team.win_percentage = 0.0
        
        # Sort teams
        ranked_teams = sorted(
            teams, 
            key=lambda t: (
                -(t.wins or 0),
                t.runs_allowed or 0
            )
        )
        
        # Create rankings with rank attribute
        rankings_data = []
        for index, team in enumerate(ranked_teams):
            team_data = team.to_dict()
            team_data['rank'] = index + 1
            
            if team.games_played > 0:
                team_data['win_percentage'] = round(team.wins / team.games_played, 3)
            else:
                team_data['win_percentage'] = 0.0
                
            rankings_data.append(team_data)
        
        return jsonify(rankings_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bracket endpoint
@app.route('/brackets', methods=['GET'])
def get_bracket():
    """DEPRECATED - Use tournament-specific bracket endpoints. 
       Get the current tournament bracket structure (legacy).
    """
    # This endpoint is now less useful as brackets are stored individually.
    # It might still be used by older parts of the app, so keep it simple.
    # It could fetch the *first* stored bracket for the tournament, or just return empty.
    # For now, let's just return an empty structure to avoid breaking things, 
    # but ideally, the frontend should call the new endpoints.
    
    tournament_id = request.args.get('tournament_id')
    
    # Return a default empty structure or potentially the first bracket if needed
    if tournament_id:
        first_bracket = TournamentBracketStorage.query.filter_by(tournament_id=tournament_id).first()
        if first_bracket:
            try:
                return jsonify(json.loads(first_bracket.bracket_json))
            except json.JSONDecodeError:
                 return jsonify({"error": "Stored bracket JSON is invalid"}), 500

    # Fallback to empty
    return jsonify({"rounds": {}}) 

@app.route('/brackets/generate', methods=['POST'])
def generate_bracket():
    """Generate a new tournament bracket with proper seeding for a 6-team format"""
    try:
        data = request.get_json()
        tournament_id = data.get('tournament_id') if data else None
        
        # Filter by tournament_id if provided
        bracket_query = BracketMatch.query
        game_query = Game.query.filter_by(game_type='Bracket')
        team_query = Team.query
        
        if tournament_id:
            bracket_query = bracket_query.filter_by(tournament_id=tournament_id)
            game_query = game_query.filter_by(tournament_id=tournament_id)
            team_query = team_query.filter_by(tournament_id=tournament_id)
        
        # Clear existing bracket data
        bracket_query.delete()
        
        # Delete any existing bracket games
        game_query.delete()
        
        db.session.commit()
        
        # Fetch teams ranked by win percentage
        teams = team_query.all()
        
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
        if len(seeded_teams) < 6:
            return jsonify({"error": "Not enough teams to create a 6-team bracket. Add at least 6 teams."}), 400
        
        # Limit to 6 teams
        seeded_teams = seeded_teams[:6]
        
        # Create bracket matches
        match_id = 1
        current_date = datetime.now().date()  # Default date for bracket games
        
        # Create Round 1: (3 vs 6) and (4 vs 5)
        # Match 1: Seed 3 vs Seed 6
        match1 = BracketMatch(
            match_display_id=match_id,
            round_number=1,
            team1_id=seeded_teams[2].id,  # Seed 3
            team2_id=seeded_teams[5].id,  # Seed 6
            team1_score=None,
            team2_score=None,
            team1_seed=3,
            team2_seed=6,
            winner_id=None,
            status='Scheduled',
            tournament_id=tournament_id
        )
        
        db.session.add(match1)
        
        # Create a corresponding game in the schedule
        game1 = Game(
            team1_id=seeded_teams[2].id,
            team2_id=seeded_teams[5].id,
            date=current_date,
            time=datetime.strptime('12:00', '%H:%M').time(),
            field='Bracket Field',
            status='Scheduled',
            game_type='Bracket',
            bracket_match_id=match_id,
            tournament_id=tournament_id
        )
        db.session.add(game1)
        
        match_id += 1
        
        # Match 2: Seed 4 vs Seed 5
        match2 = BracketMatch(
            match_display_id=match_id,
            round_number=1,
            team1_id=seeded_teams[3].id,  # Seed 4
            team2_id=seeded_teams[4].id,  # Seed 5
            team1_score=None,
            team2_score=None,
            team1_seed=4,
            team2_seed=5,
            winner_id=None,
            status='Scheduled',
            tournament_id=tournament_id
        )
        
        db.session.add(match2)
        
        # Create a corresponding game in the schedule
        game2 = Game(
            team1_id=seeded_teams[3].id,
            team2_id=seeded_teams[4].id,
            date=current_date,
            time=datetime.strptime('14:00', '%H:%M').time(),
            field='Bracket Field',
            status='Scheduled',
            game_type='Bracket',
            bracket_match_id=match_id,
            tournament_id=tournament_id
        )
        db.session.add(game2)
        
        match_id += 1
        
        # Create Round 2: (Winner of 3 vs 6 plays 1) and (Winner of 4 vs 5 plays 2)
        # Match 3: Seed 1 vs Winner of Match 1
        match3 = BracketMatch(
            match_display_id=match_id,
            round_number=2,
            team1_id=seeded_teams[0].id,  # Seed 1
            team2_id=None,  # Will be filled with winner of Match 1
            team1_score=None,
            team2_score=None,
            team1_seed=1,
            team2_seed=None,  # Will be filled later
            winner_id=None,
            status='Pending',
            tournament_id=tournament_id
        )
        
        db.session.add(match3)
        match_id += 1
        
        # Match 4: Seed 2 vs Winner of Match 2
        match4 = BracketMatch(
            match_display_id=match_id,
            round_number=2,
            team1_id=seeded_teams[1].id,  # Seed 2
            team2_id=None,  # Will be filled with winner of Match 2
            team1_score=None,
            team2_score=None,
            team1_seed=2,
            team2_seed=None,  # Will be filled later
            winner_id=None,
            status='Pending',
            tournament_id=tournament_id
        )
        
        db.session.add(match4)
        match_id += 1
        
        # Create Round 3: Championship match between winners of Round 2
        match5 = BracketMatch(
            match_display_id=match_id,
            round_number=3,
            team1_id=None,  # Will be filled with winner of Match 3
            team2_id=None,  # Will be filled with winner of Match 4
            team1_score=None,
            team2_score=None,
            team1_seed=None,  # Will be filled later
            team2_seed=None,  # Will be filled later
            winner_id=None,
            status='Pending',
            tournament_id=tournament_id
        )
        
        db.session.add(match5)
        
        db.session.commit()
        
        # Return the generated bracket
        return get_bracket()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/brackets/clear', methods=['POST'])
def clear_bracket():
    """Clear the tournament bracket without generating a new one"""
    try:
        # Delete all bracket matches
        bracket_query = BracketMatch.query
        data = request.get_json()
        tournament_id = data.get('tournament_id') if data else None
        
        if tournament_id:
            bracket_query = bracket_query.filter_by(tournament_id=tournament_id)
        
        bracket_query.delete()
        db.session.commit()
        
        # Return empty bracket structure
        return jsonify({"message": "Tournament bracket cleared successfully", "rounds": {}})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/brackets/match/<int:match_id>', methods=['PATCH'])
def update_bracket_match(match_id):
    """Update a bracket match score and advance winner according to the 6-team bracket format"""
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
            winner_seed = match.team1_seed
        elif team2_score > team1_score:
            match.winner_id = match.team2_id
            winner_seed = match.team2_seed
        else:
            return jsonify({"error": "There must be a winner in bracket play"}), 400
        
        # Update the corresponding game in the schedule
        game = Game.query.filter_by(bracket_match_id=match_id).first()
        if game:
            game.team1_score = team1_score
            game.team2_score = team2_score
            game.status = 'Completed'
            
        # Advance the winner to the next round based on our 6-team format
        next_match = None
        next_match_position = None
        
        # For the custom 6-team bracket:
        # Match 1 (3 vs 6) winner goes to Match 3 as team2 to play seed 1
        # Match 2 (4 vs 5) winner goes to Match 4 as team2 to play seed 2
        # Match 3 winner goes to Match 5 as team1
        # Match 4 winner goes to Match 5 as team2
        
        if match.round_number == 1:
            if match.match_display_id == 1:  # Match 1 (3 vs 6)
                next_match = BracketMatch.query.filter_by(match_display_id=3).first()  # Match 3
                next_match_position = 1  # Team 2 position
            elif match.match_display_id == 2:  # Match 2 (4 vs 5)
                next_match = BracketMatch.query.filter_by(match_display_id=4).first()  # Match 4
                next_match_position = 1  # Team 2 position
        elif match.round_number == 2:
            if match.match_display_id == 3:  # Match 3 (1 vs winner of 3/6)
                next_match = BracketMatch.query.filter_by(match_display_id=5).first()  # Match 5
                next_match_position = 0  # Team 1 position
            elif match.match_display_id == 4:  # Match 4 (2 vs winner of 4/5)
                next_match = BracketMatch.query.filter_by(match_display_id=5).first()  # Match 5
                next_match_position = 1  # Team 2 position
        
        # If there is a next match, advance the winner
        if next_match:
            winner_team = Team.query.get(match.winner_id)
            
            if next_match_position == 0:  # Team 1 position
                next_match.team1_id = match.winner_id
                next_match.team1_seed = winner_seed
            else:  # Team 2 position
                next_match.team2_id = match.winner_id
                next_match.team2_seed = winner_seed
                
            # If both teams are assigned, update status and create game
            if next_match.team1_id is not None and next_match.team2_id is not None:
                next_match.status = 'Scheduled'
                
                # Create a game in the schedule for the next match
                existing_game = Game.query.filter_by(bracket_match_id=next_match.match_display_id).first()
                
                if not existing_game:
                    # Get the team objects for the game
                    team1 = Team.query.get(next_match.team1_id)
                    team2 = Team.query.get(next_match.team2_id)
                    
                    if team1 and team2:
                        game = Game(
                            team1_id=next_match.team1_id,
                            team2_id=next_match.team2_id,
                            date=datetime.now().date(),
                            time=datetime.strptime('12:00', '%H:%M').time(),  # Default time
                            field='Bracket Field',
                            status='Scheduled',
                            game_type='Bracket',
                            bracket_match_id=next_match.match_display_id,
                            tournament_id=tournament_id
                        )
                        db.session.add(game)
        
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
    tournament_id = request.args.get('tournament_id')
    query = Game.query
    
    if tournament_id:
        query = query.filter_by(tournament_id=tournament_id)
    
    games = query.all()
    return jsonify([game.to_dict() for game in games])

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
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['team1_id', 'team2_id', 'date', 'time', 'field']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Parse date and time
        date_obj = None
        time_obj = None
        
        try:
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
            time_obj = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."}), 400
        
        # Create new game
        new_game = Game(
            team1_id=data['team1_id'],
            team2_id=data['team2_id'],
            date=date_obj,
            time=time_obj,
            field=data['field'],
            status=data.get('status', 'Scheduled'),
            team1_score=data.get('team1_score'),
            team2_score=data.get('team2_score'),
            game_type=data.get('game_type', 'Pool Play'),
            bracket_match_id=data.get('bracket_match_id'),
            tournament_id=data.get('tournament_id')
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
    try:
        tournament_id = request.args.get('tournament_id')
        
        # If tournament_id is provided, get settings for that tournament
        # Otherwise, get the first settings record
        if tournament_id:
            settings = TournamentSettings.query.filter_by(tournament_id=tournament_id).first()
        else:
            settings = TournamentSettings.query.first()
            
        if not settings and tournament_id:
            # If no settings exist for this tournament, create default settings
            settings = TournamentSettings(
                name="Baseball Tournament",
                tournament_id=tournament_id
            )
            db.session.add(settings)
            db.session.commit()
        elif not settings:
            # If no settings exist at all, create default settings
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
        tournament_id = data.get('tournament_id')
        
        # Get settings for specific tournament if ID provided
        if tournament_id:
            settings = TournamentSettings.query.filter_by(tournament_id=tournament_id).first()
            
            if not settings:
                # Create new settings for this tournament if they don't exist
                settings = TournamentSettings(tournament_id=tournament_id)
                db.session.add(settings)
        else:
            # Fallback to default settings (first record) if no tournament_id provided
            settings = TournamentSettings.query.first()
            if not settings:
                settings = TournamentSettings()
                db.session.add(settings)
        
        # Update fields if they exist in the request
        if 'name' in data:
            settings.name = data['name']
        
        if 'description' in data:
            settings.description = data['description']
        
        # Handle admin password
        if 'adminPassword' in data:
            settings.admin_password = data['adminPassword']
        elif 'admin_password' in data:  # Support both naming conventions
            settings.admin_password = data['admin_password']
        
        # Update tournament_id if provided and different from current
        if tournament_id and settings.tournament_id != tournament_id:
            settings.tournament_id = tournament_id
        
        db.session.commit()
        return jsonify(settings.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/reset', methods=['POST'])
def reset_tournament():
    """Reset the entire tournament, clearing all teams, games, brackets, and schedules"""
    try:
        # Delete all data in the correct order to avoid foreign key constraints
        # First, delete all games (both regular and bracket)
        Game.query.delete()
        
        # Delete all bracket matches
        BracketMatch.query.delete()
        
        # Delete all teams
        Team.query.delete()
        
        # Reset tournament settings to default (but keep the record)
        settings = TournamentSettings.query.first()
        if settings:
            settings.name = "Baseball Tournament"
            settings.description = ""
            # Keep the admin password as is
        
        db.session.commit()
        return jsonify({"message": "Tournament successfully reset to initial state"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Tournament routes
@app.route('/api/tournaments', methods=['GET'])
def get_tournaments():
    try:
        tournaments = Tournament.query.all()
        return jsonify([tournament.to_dict() for tournament in tournaments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tournaments/<int:tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    try:
        tournament = Tournament.query.get_or_404(tournament_id)
        return jsonify(tournament.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tournaments', methods=['POST'])
def create_tournament():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check if name is present
        if 'name' not in data:
            return jsonify({"error": "Tournament name is required"}), 400
            
        # Parse dates safely
        start_date = None
        end_date = None
        
        if data.get('start_date'):
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid start date format. Use YYYY-MM-DD."}), 400
                
        if data.get('end_date'):
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid end date format. Use YYYY-MM-DD."}), 400
            
        # Create new tournament
        new_tournament = Tournament(
            name=data['name'],
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            location=data.get('location'),
            status=data.get('status', 'Active')
        )
        
        db.session.add(new_tournament)
        
        # Create default tournament settings
        settings = TournamentSettings(
            name=data.get('name'),
            description=data.get('description'),
            admin_password=data.get('admin_password')
        )
        new_tournament.settings = settings
        
        db.session.commit()
        return jsonify(new_tournament.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/tournaments/<int:tournament_id>', methods=['PUT'])
def update_tournament(tournament_id):
    try:
        tournament = Tournament.query.get_or_404(tournament_id)
        data = request.get_json()
        
        if 'name' in data:
            tournament.name = data['name']
        if 'description' in data:
            tournament.description = data['description']
            
        # Parse dates safely
        if 'start_date' in data:
            if data['start_date']:
                try:
                    tournament.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"error": "Invalid start date format. Use YYYY-MM-DD."}), 400
            else:
                tournament.start_date = None
                
        if 'end_date' in data:
            if data['end_date']:
                try:
                    tournament.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"error": "Invalid end date format. Use YYYY-MM-DD."}), 400
            else:
                tournament.end_date = None
                
        if 'location' in data:
            tournament.location = data['location']
        if 'status' in data:
            tournament.status = data['status']
            
        db.session.commit()
        return jsonify(tournament.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/tournaments/<int:tournament_id>', methods=['DELETE'])
def delete_tournament(tournament_id):
    try:
        tournament = Tournament.query.get_or_404(tournament_id)
        db.session.delete(tournament)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- NEW RESTful Bracket Storage Endpoints --- 

# GET all brackets for a specific tournament
@app.route('/api/tournaments/<int:tournament_id>/brackets', methods=['GET'])
def get_tournament_brackets(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    brackets = TournamentBracketStorage.query.filter_by(tournament_id=tournament.id).order_by(TournamentBracketStorage.name).all()
    return jsonify([bracket.to_dict() for bracket in brackets])

# POST - Create a new bracket for a tournament
@app.route('/api/tournaments/<int:tournament_id>/brackets', methods=['POST'])
def create_tournament_bracket(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.get_json()

    if not data or 'name' not in data or 'bracket_json' not in data:
        return jsonify({"error": "Missing required fields: name, bracket_json"}), 400

    bracket_json_str = data['bracket_json']
    bracket_name = data['name']

    # Validate JSON
    try:
        json.loads(bracket_json_str)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    new_bracket = TournamentBracketStorage(
        name=bracket_name,
        bracket_json=bracket_json_str,
        tournament_id=tournament.id
    )
    db.session.add(new_bracket)
    try:
        db.session.commit()
        return jsonify(new_bracket.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET a specific bracket by its ID
@app.route('/api/brackets/<int:bracket_id>', methods=['GET'])
def get_single_bracket(bracket_id):
    bracket = TournamentBracketStorage.query.get_or_404(bracket_id)
    return jsonify(bracket.to_dict())

# PUT - Update a specific bracket by its ID
@app.route('/api/brackets/<int:bracket_id>', methods=['PUT'])
def update_bracket(bracket_id):
    bracket = TournamentBracketStorage.query.get_or_404(bracket_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'name' in data:
        bracket.name = data['name']
    
    if 'bracket_json' in data:
        bracket_json_str = data['bracket_json']
        # Validate JSON
        try:
            json.loads(bracket_json_str)
            bracket.bracket_json = bracket_json_str
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
    
    bracket.updated_at = datetime.now()
    
    try:
        db.session.commit()
        return jsonify(bracket.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# DELETE a specific bracket by its ID
@app.route('/api/brackets/<int:bracket_id>', methods=['DELETE'])
def delete_bracket(bracket_id):
    bracket = TournamentBracketStorage.query.get_or_404(bracket_id)
    try:
        db.session.delete(bracket)
        db.session.commit()
        return jsonify({"message": f"Bracket '{bracket.name}' deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
