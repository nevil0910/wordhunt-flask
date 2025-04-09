# WordHunt Game

A word search game built with Flask that runs with SQLite database.

## Features

- Multiple difficulty levels: Easy, Normal, and Hard
- User authentication and leaderboards
- Email verification for account security
- Responsive design for desktop and mobile play

## Local Development Setup

1. Clone the repository:
```
git clone https://github.com/yourusername/wordhunt.git
cd wordhunt
```

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory with these settings:
```
SECRET_KEY=your_secret_key_here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password
```

For Gmail users, you'll need to:
1. Enable 2-Factor Authentication in your Google account
2. Create an App Password specifically for this application
3. Use that App Password in the `.env` file

6. Run the application:
```
python app.py
```

7. Access the application in your browser at http://localhost:5000

## Deployment with SQLite

You can deploy this application with the existing SQLite database. Here are instructions for different platforms:

### Deployment to a VPS or Dedicated Server

1. Transfer your code to the server (using Git, SCP, or SFTP)
2. Install Python and required dependencies
3. Set up your environment variables in a `.env` file
4. Run the application with Gunicorn:
```
gunicorn wsgi:app
```

### Deployment to Render

1. Push your code to GitHub
2. Create a new Web Service in Render
3. Connect to your GitHub repository
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `gunicorn wsgi:app`
6. Set the following environment variables:
   ```
   SECRET_KEY=your_secure_random_key
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   RENDER=true
   ```

The database will be stored in the `instance` directory within your application, which is automatically created when the application starts. This ensures that your database will be accessible to the application without requiring special permissions.

Note that with Render's free tier, the disk is ephemeral, meaning your database may be reset when your service is restarted or redeployed. For a production application, consider using Render's paid tier with a persistent disk or migrate to a hosted database service.

### Important Notes for SQLite in Production

- SQLite is file-based, so your database will be stored in the file system
- Make sure your deployment platform persists the database file
- For low-to-medium traffic, SQLite can handle the load well
- For higher traffic, consider migrating to PostgreSQL or MySQL

## Using a PostgreSQL Database (Recommended for Production)

To use an external PostgreSQL database with WordHunt (which will persist data even when your Render service spins down):

1. Create a free PostgreSQL database:
   - [Supabase](https://supabase.com/) - 500MB free database
   - [Neon](https://neon.tech/) - 3GB free database
   - [ElephantSQL](https://www.elephantsql.com/) - 20MB free database (Tiny Turtle plan)

2. Get your PostgreSQL connection string, which will look like:
   ```
   postgresql://username:password@hostname:port/database
   ```

3. Add the connection string to your `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@hostname:port/database
   ```

4. If deploying on Render, add the `DATABASE_URL` as an environment variable in your service settings.

5. To migrate existing data from SQLite to PostgreSQL:
   ```
   python migrate_to_postgres.py
   ```

6. Restart your application:
   ```
   python app.py
   ```

The application will automatically detect the PostgreSQL database URL and use it instead of SQLite.

## Game Instructions

1. Register an account and verify your email
2. Log in to your account
3. Choose a difficulty level:
   - Easy: 5x5 grid with 3-4 letter words
   - Normal: 10x10 grid with 6-7 letter words
   - Hard: 15x15 grid with 8-10 letter words
4. Find words in the grid by clicking and dragging
5. Try to find all hidden words to maximize your score!

## License

This project is licensed under the MIT License.