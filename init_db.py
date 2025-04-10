import os
import sys
import time

os.environ['RENDER'] = 'true'

print("Initializing database...")
print(f"Current directory: {os.getcwd()}")

# Try to import the app and create the tables
try:
    from app import app, db, User, Score
    
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        
        # Verify tables were created
        table_names = db.inspect(db.engine).get_table_names()
        print(f"Tables created: {table_names}")
        
        # Check if tables exist
        if 'user' not in table_names:
            print("User table not found, trying alternative approach...")
            # Try to create tables explicitly
            try:
                db.metadata.tables['user'].create(db.engine)
                db.metadata.tables['score'].create(db.engine)
            except Exception as e:
                print(f"Error in explicit table creation: {e}")
            
            # Check again after explicit creation
            table_names = db.inspect(db.engine).get_table_names()
            print(f"Tables after explicit creation: {table_names}")
        
        print("Database initialization completed successfully!")
except Exception as e:
    print(f"Error initializing database: {e}")
    sys.exit(1)

# Verify the tables in the database
try:
    print("\nVerifying database tables...")
    with app.app_context():
        # Check for tables
        table_names = db.inspect(db.engine).get_table_names()
        print(f"Tables in database: {table_names}")
        
        user_count = User.query.count()
        print(f"Number of users in database: {user_count}")
        
        score_count = Score.query.count()
        print(f"Number of scores in database: {score_count}")
        
        print("Database verification completed successfully!")
except Exception as e:
    print(f"Error verifying database: {e}")
    sys.exit(1)

print("Database setup completed successfully!")
sys.exit(0)