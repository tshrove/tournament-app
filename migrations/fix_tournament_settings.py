"""
Migration script to fix the tournament_settings table by recreating it with the tournament_id column
"""

import sqlite3
import os
import sys
from datetime import datetime

# Get the database file path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/instance/tournament.db'))

def run_migration():
    print(f"Starting tournament_settings table fix on database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file doesn't exist at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get the default tournament ID
        cursor.execute("SELECT id FROM tournament LIMIT 1")
        result = cursor.fetchone()
        default_tournament_id = result[0] if result else None
        
        if not default_tournament_id:
            print("No tournaments found. Creating a default one...")
            cursor.execute('''
            INSERT INTO tournament (name, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', ('Default Tournament', 'Default tournament created during migration', 'Active', 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            default_tournament_id = cursor.lastrowid
            print(f"Default tournament created with ID: {default_tournament_id}")
        
        print("Force-recreating tournament_settings table...")
        
        # First, backup the current data if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament_settings'")
        if cursor.fetchone():
            try:
                cursor.execute("SELECT id, name, description, admin_password, updated_at FROM tournament_settings")
                settings_data = cursor.fetchall()
                print(f"Found {len(settings_data)} existing settings records to migrate")
            except sqlite3.OperationalError:
                # In case the structure is different than expected
                print("Couldn't read existing settings data with expected columns, starting fresh")
                settings_data = []
        else:
            settings_data = []
            print("No existing tournament_settings table found")
        
        # Drop the old table
        cursor.execute("DROP TABLE IF EXISTS tournament_settings")
        
        # Create a new table with the correct schema
        cursor.execute('''
        CREATE TABLE tournament_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            admin_password TEXT,
            updated_at TIMESTAMP,
            tournament_id INTEGER REFERENCES tournament(id)
        )
        ''')
        
        # Restore the data with the default tournament_id
        for settings in settings_data:
            cursor.execute('''
            INSERT INTO tournament_settings (id, name, description, admin_password, updated_at, tournament_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (settings[0], settings[1], settings[2], settings[3], settings[4], default_tournament_id))
        
        print(f"Tournament settings updated with tournament_id={default_tournament_id}")
        
        # Verify the new structure
        cursor.execute('PRAGMA table_info(tournament_settings)')
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Verified columns in tournament_settings: {', '.join(columns)}")
        
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