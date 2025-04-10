echo "Starting database setup..."

# Get application directory
APP_DIR=$(pwd)
INSTANCE_DIR="${APP_DIR}/instance"

echo "Creating instance directory at ${INSTANCE_DIR}"
mkdir -p "${INSTANCE_DIR}"

# Ensure proper permissions
chmod -R 755 "${INSTANCE_DIR}"

# Verify Python environment
echo "Python version:"
python --version

# Create empty database file if it doesn't exist
DB_FILE="${INSTANCE_DIR}/wordhunt.db"
if [ ! -f "${DB_FILE}" ]; then
    echo "Creating empty database file at ${DB_FILE}..."
    touch "${DB_FILE}"
    chmod 664 "${DB_FILE}"
fi

# Run a Python script to initialize the database
echo "Initializing database schema..."
python <<EOF
import os
os.environ['RENDER'] = 'true'
from app import app, db, User, Score

with app.app_context():
    db.create_all()
    print("Database tables created successfully")
    
    # Print table names
    table_names = db.inspect(db.engine).get_table_names()
    print(f"Tables in database: {table_names}")
    
    # Verify User table exists
    if 'user' not in table_names:
        print("WARNING: user table not found, trying explicit creation")
        db.metadata.tables['user'].create(db.engine)
    
    # Check again
    table_names = db.inspect(db.engine).get_table_names()
    print(f"Final tables in database: {table_names}")
EOF

# Verify database file exists and has content
echo "Database file status:"
ls -la "${DB_FILE}" || echo "Database file not found!"
file "${DB_FILE}" || echo "Could not check file type"
echo "Database setup completed" 