# WordHunt Game

A word search puzzle game built with Python Flask, featuring multiple difficulty levels and user authentication.

## Live Demo

**The project is deployed on Render until May 8, 2025.**

🔗 **Play Now**: [https://wordhunt-game.onrender.com/](https://wordhunt-game.onrender.com/)

> **Note**: The game currently has compatibility issues with mobile devices. The SVG line drawing feature for word selection does not work properly on mobile browsers. For the best experience, please use a desktop browser.

## Features

- **Multiple Difficulty Levels**: 
  - Easy (5×5 grid, shorter words)
  - Normal (10×10 grid, medium words)
  - Hard (15×15 grid, longer words)
- **User System**: Secure authentication with email verification
- **Leaderboards**: Track top scores across all difficulty levels
- **Responsive Design**: Optimized for desktop play.

## Local Development Setup

1. Clone the repository:
```
git clone https://github.com/nevil0910/wordhunt-flask.git
cd wordhunt-flask
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

5. Create a `.env` file in the root directory:
```
SECRET_KEY=your_secret_key_here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

For Gmail users:
1. Enable 2-Factor Authentication in your Google account
2. Create an App Password specifically for this application
3. Use that App Password in the `.env` file

6. Run the application:
```
python app.py
```

7. Access the application at http://localhost:5000

## Deployment Options

### Render Deployment (Current Method)

1. Fork the repository to your GitHub account
2. Create a new Web Service on [Render](https://render.com/)
3. Connect to your GitHub repository
4. Configure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:app`
   - Environment variables:
     ```
     SECRET_KEY=your_secure_random_key
     MAIL_SERVER=smtp.gmail.com
     MAIL_PORT=587
     MAIL_USE_TLS=True
     MAIL_USERNAME=your_email@gmail.com
     MAIL_PASSWORD=your_app_password
     RENDER=true
     ```

### Database Options

#### SQLite (Default)
- Automatically used if no external database is configured
- Stored in the `instance` directory
- Simple setup but data may be lost on some hosting platforms

#### PostgreSQL (Recommended for Production)
1. Create a PostgreSQL database with any provider:
   - [Supabase](https://supabase.com/) (500MB free)
   - [Neon](https://neon.tech/) (3GB free)
   - [ElephantSQL](https://www.elephantsql.com/) (20MB free)

2. Set your database URL as an environment variable:
   ```
   DATABASE_URL=postgresql://username:password@hostname:port/database
   ```

3. To migrate existing data to PostgreSQL:
   ```
   python migrate_to_postgres.py
   ```

## How to Play

1. Register an account and verify your email
2. Log in to your account
3. Select your preferred difficulty level
4. Find words in the grid by clicking and dragging (desktop recommended)
5. Discover all hidden words before time runs out!

## Known Issues

- SVG line drawing for word selection doesn't work properly on mobile devices
- For the best gameplay experience, a desktop browser is recommended

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.