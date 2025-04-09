# WordHunt Game

A word search game built with Flask that can be deployed on Render.

## Features

- Multiple difficulty levels: Easy, Normal, and Hard
- User authentication and leaderboards
- Email verification for account security
- Responsive design for desktop and mobile play

## Deployment to Render

### Automatic Deployment

1. Fork this repository to your GitHub account
2. Sign up for a [Render](https://render.com/) account
3. Create a new "Blueprint" in Render and connect to your GitHub repository
4. Render will automatically detect the `render.yaml` configuration file and deploy the service and database

### Manual Deployment

1. Create a new Web Service in Render
2. Connect your GitHub repository
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
   - Python Version: 3.9
4. Add the following environment variables:
   - `SECRET_KEY`: Generate a random secure string
   - `DATABASE_URL`: Your PostgreSQL database URL (Render will provide this if you create a PostgreSQL database)
   - For email functionality:
     - `MAIL_USERNAME`: Your email username
     - `MAIL_PASSWORD`: Your email password or app password
     - `MAIL_SERVER`: SMTP server (default: smtp.gmail.com)
     - `MAIL_PORT`: SMTP port (default: 587)
     - `MAIL_USE_TLS`: True or False

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with the necessary environment variables
6. Run the application: `python wsgi.py`

## Database Migrations

When making changes to the database models:

1. Initialize migrations if not already done: `flask db init`
2. Create a migration: `flask db migrate -m "Description of changes"`
3. Apply the migration: `flask db upgrade`

## License

This project is licensed under the MIT License.