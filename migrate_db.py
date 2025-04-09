"""
Script to migrate data from SQLite to PostgreSQL database.
Run this script when you need to transfer data from local development
to production database on Render.
"""

import os
import sqlite3
import psycopg2
from dotenv import load_dotenv
from app import app, db

load_dotenv()

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Check if PostgreSQL database URL is available
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL environment variable not set.")
        return False
    
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Connect to SQLite database
        sqlite_conn = sqlite3.connect('wordhunt.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL database
        pg_conn = psycopg2.connect(db_url)
        pg_cursor = pg_conn.cursor()
        
        # Get all tables from SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cursor.fetchall()
        
        # Migrate each table
        for table in tables:
            table_name = table[0]
            
            # Skip SQLite internal tables
            if table_name.startswith('sqlite_'):
                continue
                
            print(f"Migrating table: {table_name}")
            
            # Get table schema
            sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
            columns = sqlite_cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # Get data from SQLite table
            sqlite_cursor.execute(f"SELECT * FROM {table_name};")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"No data in table {table_name}")
                continue
            
            # Clear PostgreSQL table
            try:
                pg_cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
                pg_conn.commit()
            except Exception as e:
                print(f"Could not truncate table {table_name}: {e}")
                pg_conn.rollback()
            
            # Insert data into PostgreSQL table
            for row in rows:
                placeholders = ', '.join(['%s'] * len(row))
                columns_str = ', '.join(column_names)
                
                try:
                    pg_cursor.execute(
                        f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});",
                        row
                    )
                except Exception as e:
                    print(f"Error inserting row into {table_name}: {e}")
                    pg_conn.rollback()
                    continue
            
            pg_conn.commit()
            print(f"Successfully migrated {len(rows)} rows from {table_name}")
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    finally:
        # Close connections
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == '__main__':
    # Create tables in PostgreSQL if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created or confirmed to exist.")
    
    # Migrate data
    success = migrate_sqlite_to_postgres()
    if success:
        print("Data migration completed successfully.")
    else:
        print("Data migration failed. Check the error messages above.") 