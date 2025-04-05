"""
Migration script to add Tournament table and update existing models to reference tournaments
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Get the database file path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/instance/tournament.db'))

def run_migration():
    print(f"Starting migration on database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file doesn't exist at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create Tournament table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournament (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date DATE,
            end_date DATE,
            location TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Check if Tournament table is empty
        cursor.execute("SELECT COUNT(*) FROM tournament")
        count = cursor.fetchone()[0]
        
        # Create a default tournament if none exists
        if count == 0:
            print("Creating default tournament...")
            cursor.execute('''
            INSERT INTO tournament (name, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', ('Default Tournament', 'Default tournament created during migration', 'Active', 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            default_tournament_id = cursor.lastrowid
            print(f"Default tournament created with ID: {default_tournament_id}")
        else:
            # Get the first tournament ID if any exist
            cursor.execute("SELECT id FROM tournament LIMIT 1")
            default_tournament_id = cursor.fetchone()[0]
        
        # Add tournament_id column to Team table if it doesn't exist
        cursor.execute('PRAGMA table_info(team)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tournament_id' not in columns:
            print("Adding tournament_id to team table...")
            cursor.execute('ALTER TABLE team ADD COLUMN tournament_id INTEGER REFERENCES tournament(id)')
            cursor.execute(f'UPDATE team SET tournament_id = {default_tournament_id}')
        
        # Add tournament_id column to Game table if it doesn't exist
        cursor.execute('PRAGMA table_info(game)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tournament_id' not in columns:
            print("Adding tournament_id to game table...")
            cursor.execute('ALTER TABLE game ADD COLUMN tournament_id INTEGER REFERENCES tournament(id)')
            cursor.execute(f'UPDATE game SET tournament_id = {default_tournament_id}')
        
        # Add tournament_id column to BracketMatch table if it doesn't exist
        cursor.execute('PRAGMA table_info(bracket_match)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tournament_id' not in columns:
            print("Adding tournament_id to bracket_match table...")
            cursor.execute('ALTER TABLE bracket_match ADD COLUMN tournament_id INTEGER REFERENCES tournament(id)')
            cursor.execute(f'UPDATE bracket_match SET tournament_id = {default_tournament_id}')
            
            # Remove the unique constraint on match_display_id
            # SQLite doesn't support dropping constraints, so we need to recreate the table
            print("Recreating bracket_match table to remove unique constraint on match_display_id...")
            cursor.execute('''
            CREATE TABLE bracket_match_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_display_id INTEGER NOT NULL,
                round_number INTEGER NOT NULL,
                team1_id INTEGER REFERENCES team(id),
                team2_id INTEGER REFERENCES team(id),
                team1_score INTEGER,
                team2_score INTEGER,
                team1_seed INTEGER,
                team2_seed INTEGER,
                winner_id INTEGER REFERENCES team(id),
                status TEXT DEFAULT 'Scheduled',
                tournament_id INTEGER REFERENCES tournament(id)
            )
            ''')
            
            cursor.execute('''
            INSERT INTO bracket_match_new 
            SELECT id, match_display_id, round_number, team1_id, team2_id, 
                   team1_score, team2_score, team1_seed, team2_seed, winner_id, status, tournament_id 
            FROM bracket_match
            ''')
            
            cursor.execute('DROP TABLE bracket_match')
            cursor.execute('ALTER TABLE bracket_match_new RENAME TO bracket_match')
        
        # Add tournament_id column to Bracket table if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bracket'")
        if cursor.fetchone():
            cursor.execute('PRAGMA table_info(bracket)')
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'tournament_id' not in columns:
                print("Adding tournament_id to bracket table...")
                cursor.execute('ALTER TABLE bracket ADD COLUMN tournament_id INTEGER REFERENCES tournament(id)')
                cursor.execute(f'UPDATE bracket SET tournament_id = {default_tournament_id}')
        
        # Add tournament_id column to TournamentSettings table if it doesn't exist
        cursor.execute('PRAGMA table_info(tournament_settings)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tournament_id' not in columns:
            print("Adding tournament_id to tournament_settings table...")
            cursor.execute('ALTER TABLE tournament_settings ADD COLUMN tournament_id INTEGER REFERENCES tournament(id)')
            cursor.execute(f'UPDATE tournament_settings SET tournament_id = {default_tournament_id}')
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration() 