from app import app, db
import os

# Create database tables if they don't exist yet
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Run the app with Gunicorn in production (handled by Render)
    # For local testing only:
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 