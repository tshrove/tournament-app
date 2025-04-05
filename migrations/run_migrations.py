#!/usr/bin/env python3
"""
Script to run all migrations in sequence
"""

import os
import sys
import importlib.util
from datetime import datetime

def run_migrations():
    print(f"Starting migrations at {datetime.now().isoformat()}")
    
    # Get the migrations directory
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all Python files in the migrations directory except this one
    migration_files = [f for f in os.listdir(migrations_dir) 
                      if f.endswith('.py') and f != 'run_migrations.py' and f != '__init__.py']
    
    # Sort migration files to ensure they run in a sensible order
    migration_files.sort()
    
    for migration_file in migration_files:
        migration_path = os.path.join(migrations_dir, migration_file)
        
        print(f"\nRunning migration: {migration_file}")
        
        try:
            # Dynamically import the migration module
            spec = importlib.util.spec_from_file_location("migration", migration_path)
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            
            # Run the migration
            if hasattr(migration, 'run_migration'):
                migration.run_migration()
            else:
                print(f"Error: {migration_file} doesn't have a run_migration() function")
        except Exception as e:
            print(f"Error running migration {migration_file}: {str(e)}")
    
    print(f"\nAll migrations completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    run_migrations() 