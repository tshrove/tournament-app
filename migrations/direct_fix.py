"""
Direct database fix to recreate the tournament_settings table
"""

import sqlite3
import os
import datetime
import sys

# Get the database file path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/instance/tournament.db'))

def run_migration():
    print(f"Starting direct database fix on: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file doesn't exist at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # STEP 1: Get the default tournament ID
        cursor.execute("SELECT id FROM tournament LIMIT 1")
        result = cursor.fetchone()
        default_tournament_id = result[0] if result else 1
        
        # STEP 2: Backup existing settings data
        print("Backing up existing settings data...")
        settings_data = []
        try:
            cursor.execute("SELECT * FROM tournament_settings")
            column_names = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # Create dictionary for each row with column names
            for row in rows:
                settings_dict = {column_names[i]: row[i] for i in range(len(column_names))}
                settings_data.append(settings_dict)
                
            print(f"Backed up {len(settings_data)} settings records")
            print(f"Columns found: {', '.join(column_names)}")
        except sqlite3.OperationalError as e:
            print(f"Error accessing tournament_settings: {e}")
            print("Will create fresh settings table")
        
        # STEP 3: Drop and recreate the table
        print("Dropping tournament_settings table...")
        cursor.execute("DROP TABLE IF EXISTS tournament_settings")
        
        print("Creating new tournament_settings table...")
        cursor.execute('''
        CREATE TABLE tournament_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT 'Baseball Tournament',
            description TEXT,
            admin_password TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tournament_id INTEGER
        )
        ''')
        
        # STEP 4: Restore data or create default
        if settings_data:
            print("Restoring existing settings data...")
            for settings in settings_data:
                # Build parameters based on available columns
                # Add tournament_id if it wasn't in the original data
                if 'tournament_id' not in settings:
                    settings['tournament_id'] = default_tournament_id
                
                # Build SQL insert dynamically
                columns = ', '.join(settings.keys())
                placeholders = ', '.join(['?'] * len(settings))
                sql = f"INSERT INTO tournament_settings ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, list(settings.values()))
        else:
            print("Creating default settings record...")
            cursor.execute('''
            INSERT INTO tournament_settings (name, description, tournament_id, updated_at)
            VALUES (?, ?, ?, ?)
            ''', ('Baseball Tournament', 'Default tournament settings', default_tournament_id, 
                  datetime.datetime.now().isoformat()))
        
        # STEP 5: Verify the structure
        cursor.execute('PRAGMA table_info(tournament_settings)')
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Verified new columns: {', '.join(columns)}")
        
        # Commit and finish
        conn.commit()
        print("Database fix completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration() 