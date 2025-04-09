#!/bin/bash

# Database setup script for Render deployment

echo "Starting database setup..."

# Create data directory if it doesn't exist
mkdir -p /data

# Ensure proper permissions
chmod -R 777 /data

# Verify Python environment
echo "Python version:"
python --version

# Create empty database file if it doesn't exist
if [ ! -f "/data/wordhunt.db" ]; then
    echo "Creating empty database file..."
    touch /data/wordhunt.db
    chmod 666 /data/wordhunt.db
fi

# Run a Python script to initialize the database
echo "Initializing database schema..."
python <<EOF
from app import app, db
# Import all models to ensure they're registered with SQLAlchemy
from models import User, Word, Game, Score

with app.app_context():
    db.create_all()
    print("Database tables created successfully")
    
    # Print table names
    table_names = db.inspect(db.engine).get_table_names()
    print(f"Tables in database: {table_names}")
EOF

echo "Database setup completed" 