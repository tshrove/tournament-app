from database import db
from datetime import datetime

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    runs_scored = db.Column(db.Integer, default=0)
    runs_allowed = db.Column(db.Integer, default=0)
    run_differential = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Team {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'wins': self.wins,
            'losses': self.losses,
            'runs_scored': self.runs_scored,
            'runs_allowed': self.runs_allowed,
            'run_differential': self.run_differential,
            'games_played': self.games_played
        }

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team1_score = db.Column(db.Integer, nullable=True)
    team2_score = db.Column(db.Integer, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    field = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Completed, Cancelled
    
    # Relationships
    team1 = db.relationship('Team', foreign_keys=[team1_id], backref=db.backref('home_games', lazy=True))
    team2 = db.relationship('Team', foreign_keys=[team2_id], backref=db.backref('away_games', lazy=True))

    def __repr__(self):
        return f'<Game {self.id}: {self.team1.name} vs {self.team2.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'team1_id': self.team1_id,
            'team2_id': self.team2_id,
            'team1_name': self.team1.name if self.team1 else None,
            'team2_name': self.team2.name if self.team2 else None,
            'team1_score': self.team1_score,
            'team2_score': self.team2_score,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.isoformat() if self.time else None,
            'field': self.field,
            'status': self.status
        }

class Bracket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_display_id = db.Column(db.Integer, unique=True, nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    team1_score = db.Column(db.Integer, nullable=True)
    team2_score = db.Column(db.Integer, nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    status = db.Column(db.String(20), default='Scheduled')

    def __repr__(self):
        return f'<Bracket {self.match_display_id}>'

class BracketMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_display_id = db.Column(db.Integer, unique=True, nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    team1_score = db.Column(db.Integer, nullable=True)
    team2_score = db.Column(db.Integer, nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    status = db.Column(db.String(20), default='Scheduled')
    
    def __repr__(self):
        return f'<BracketMatch {self.match_display_id}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'matchId': self.match_display_id,
            'round': self.round_number,
            'team1_id': self.team1_id,
            'team2_id': self.team2_id,
            'team1_score': self.team1_score,
            'team2_score': self.team2_score,
            'winner_id': self.winner_id,
            'status': self.status
        }

class TournamentSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="Baseball Tournament")
    description = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<TournamentSettings {self.id}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
