from app import app, db, User, Score
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    try:
        logger.info("Checking database and creating tables if they don't exist...")
        with app.app_context():
            db.create_all()
            
            table_names = db.inspect(db.engine).get_table_names()
            
            logger.info(f"Current tables in database: {table_names}")
            
            if 'user' not in table_names:
                logger.warning("User table not created. Trying with lowercase model name...")
                db.create_all()
                
                table_names = db.inspect(db.engine).get_table_names()
                logger.info(f"Tables after second attempt: {table_names}")
                
                if 'user' not in table_names:
                    db.metadata.create_all(db.engine)
                    logger.info(f"Final attempt to create tables completed.")
                    
        logger.info("Database setup completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False

attempts = 0
max_attempts = 3

while attempts < max_attempts:
    if setup_database():
        break
    else:
        attempts += 1
        if attempts < max_attempts:
            logger.warning(f"Database setup failed, retrying in 3 seconds (attempt {attempts}/{max_attempts})...")
            time.sleep(3)
        else:
            logger.error("Failed to set up database after maximum attempts.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 