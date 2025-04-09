"""
Utility script to migrate data from local SQLite database to PostgreSQL
Run this script locally after you've set up your PostgreSQL database
"""

import os
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import sys

load_dotenv()

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Check if PostgreSQL database URL is available
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL environment variable not set.")
        print("Please set DATABASE_URL in your .env file to the PostgreSQL connection string.")
        print("Example: DATABASE_URL=postgresql://username:password@hostname:port/database")
        return False
    
    # Fix Render-style postgres:// URLs
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    # Parse the PostgreSQL connection URL
    # Format is: postgresql://username:password@hostname:port/database
    try:
        # Simple parsing, works for most standard connection strings
        if '://' in db_url:
            # Extract the parts after ://
            conn_parts = db_url.split('://', 1)[1]
            
            # Split user:pass@host:port/dbname
            creds_host, db_name = conn_parts.split('/', 1)
            
            if '@' in creds_host:
                creds, host_part = creds_host.split('@', 1)
            else:
                creds = ""
                host_part = creds_host
                
            if ':' in creds:
                user, password = creds.split(':', 1)
            else:
                user = creds
                password = ""
                
            if ':' in host_part:
                host, port = host_part.split(':', 1)
            else:
                host = host_part
                port = "5432"  # Default PostgreSQL port
        
            # Now we have the individual parts
            print(f"Connecting to PostgreSQL database:")
            print(f"  Host: {host}")
            print(f"  Port: {port}")
            print(f"  Database: {db_name}")
            print(f"  User: {user}")
            print(f"  Password: {'*' * len(password) if password else 'None'}")
        else:
            print("Could not parse DATABASE_URL. Using it directly with psycopg2.")
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        print("Will attempt to connect using the full URL directly.")
    
    try:
        # Connect to SQLite database
        print("\nConnecting to SQLite database...")
        sqlite_conn = sqlite3.connect('wordhunt.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL database
        print("Connecting to PostgreSQL database...")
        pg_conn = psycopg2.connect(db_url)
        pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        pg_cursor = pg_conn.cursor()
        
        # Get all tables from SQLite
        print("Getting tables from SQLite...")
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cursor.fetchall()
        
        print(f"Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        # Migrate each table
        for table in tables:
            table_name = table[0]
            
            # Skip SQLite internal tables
            if table_name.startswith('sqlite_'):
                continue
                
            print(f"\nMigrating table: {table_name}")
            
            # Get table schema
            sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
            columns = sqlite_cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            print(f"  Columns: {column_names}")
            
            # Get data from SQLite table
            sqlite_cursor.execute(f"SELECT * FROM {table_name};")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  No data in table {table_name}")
                continue
            
            print(f"  Found {len(rows)} rows to migrate")
            
            # Clear PostgreSQL table
            try:
                pg_cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
            except Exception as e:
                print(f"  Could not truncate table {table_name}: {e}")
                print("  Continuing without truncating")
            
            # Insert data into PostgreSQL table
            inserted = 0
            for row in rows:
                placeholders = ', '.join(['%s'] * len(row))
                columns_str = ', '.join([f'"{col}"' for col in column_names])
                
                try:
                    pg_cursor.execute(
                        f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders});',
                        row
                    )
                    inserted += 1
                except Exception as e:
                    print(f"  Error inserting row into {table_name}: {e}")
                    print(f"  Row: {row}")
                    continue
            
            print(f"  Successfully migrated {inserted} out of {len(rows)} rows from {table_name}")
        
        print("\nMigration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    finally:
        # Close connections
        if 'sqlite_conn' in locals() and sqlite_conn:
            sqlite_conn.close()
        if 'pg_conn' in locals() and pg_conn:
            pg_conn.close()

if __name__ == '__main__':
    print("=== SQLite to PostgreSQL Migration Tool ===")
    
    if not os.path.exists('wordhunt.db'):
        print("Error: wordhunt.db file not found.")
        print("Make sure you're running this script from the same directory as your SQLite database.")
        sys.exit(1)
    
    success = migrate_sqlite_to_postgres()
    if success:
        print("Data migration completed successfully.")
    else:
        print("Data migration failed. Check the error messages above.")
        sys.exit(1) 