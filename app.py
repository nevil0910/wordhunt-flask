from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import game
import os
from datetime import datetime
from sqlalchemy import func
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///wordhunt.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

def send_email(subject, recipient, plain_body, html_body):
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')
    smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('MAIL_PORT', 587))
    use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')

    if not sender_email or not sender_password:
        print("Email credentials not configured in .env file.")
        return False

    
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = f"WordHunt Team <{sender_email}>"
    message['To'] = recipient
    
    message['Reply-To'] = sender_email 

    
    part1 = MIMEText(plain_body, 'plain')
    part2 = MIMEText(html_body, 'html')

    
    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if use_tls:
                server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
            print(f"Multipart Email sent successfully to {recipient}")
            return True
    except smtplib.SMTPAuthenticationError:
        print(f"Email Authentication Error: Check credentials. Failed to send to {recipient}")
        return False
    except Exception as e:
        print(f"Error sending multipart email to {recipient}: {e}")
        return False
# --- End Email Sending Function ---

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    scores = db.relationship('Score', backref='user', lazy=True)

# Score model for leaderboard
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    words_found = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('signup'))
        
        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password),
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        new_user.otp = otp
        db.session.commit()
        
        # Prepare email content (Plain and HTML)
        subject = "Welcome to WordHunt - Verify Your Email"
        plain_body = f'''Hi {username},

Welcome to WordHunt! Thank you for signing up.

Use this One-Time Password (OTP) to verify your email address:

{otp}

Enter this code on the verification page.

Thanks,
The WordHunt Team
'''
        html_body = f'''<html><head></head><body style="font-family: sans-serif;">
<p>Hi {username},</p>
<p>Welcome to WordHunt! Thank you for signing up.</p>
<p>Please use the following One-Time Password (OTP) to verify your email address:</p>
<p style="font-size: 1.6em; font-weight: bold; margin: 25px 0; color: #4A90E2;">{otp}</p>
<p>Enter this code on the verification page to activate your account.</p>
<p>If you didn't sign up for WordHunt, please ignore this email.</p>
<p>Happy Gaming!<br>The WordHunt Team</p>
<hr style="border: none; border-top: 1px solid #eee;">
<p style="font-size: 0.8em; color: #777;">This is an automated message. Please do not reply.</p>
</body></html>'''

        # Send email using updated smtplib function
        if send_email(subject, email, plain_body, html_body):
            flash('Verification OTP sent to your email.', 'info')
            session['verification_email'] = email
            return redirect(url_for('verify_email'))
        else:
            # Email failed to send
            print(f"Failed to send signup verification email to {email}")
            flash('Could not send verification email. Please try signing up again or contact support.', 'danger')
            # Clean up the user created if email fails
            db.session.delete(new_user)
            db.session.commit()
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'verification_email' not in session:
        return redirect(url_for('signup'))
    
    email_to_verify = session['verification_email']
    user = User.query.filter_by(email=email_to_verify).first()

    if not user:
         flash('User not found. Please sign up again.', 'danger')
         session.pop('verification_email', None)
         return redirect(url_for('signup'))

    if request.method == 'POST':
        otp = request.form.get('otp')
        
        if user.otp == otp:
            user.is_verified = True
            user.otp = None
            db.session.commit()
            
            # Prepare welcome email content (Optional)
            subject = 'Welcome to WordHunt!'
            plain_body = f'''Hi {user.username},

Welcome to WordHunt! Your account is now verified.

You can log in and start playing.

Happy Gaming!
The WordHunt Team
'''
            html_body = f'''<html><body style="font-family: sans-serif;">
<p>Hi {user.username},</p>
<p>Welcome to WordHunt! Your account has been successfully verified.</p>
<p>You can now <a href="{ url_for('login', _external=True) }">log in</a> and start playing. Challenge yourself with different difficulty levels and compete for the highest scores!</p>
<p>Happy Gaming!<br>The WordHunt Team</p>
</body></html>'''
            # Send welcome email
            send_email(subject, user.email, plain_body, html_body)
            
            session.pop('verification_email', None)
            flash('Account verified successfully! You can now login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    
    return render_template('verify_email.html', email=email_to_verify)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if user.is_verified:
                login_user(user)
                return redirect(url_for('index'))
            else:
                # Resend OTP for unverified user
                otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
                user.otp = otp
                db.session.commit()
                
                subject = 'WordHunt - Verify Your Email'
                plain_body = f'''Hi {user.username},

It looks like your email isn't verified yet. Use this OTP to verify your email:

{otp}

Thanks,
The WordHunt Team
'''
                html_body = f'''<html><body style="font-family: sans-serif;">
<p>Hi {user.username},</p>
<p>It looks like your email address isn't verified yet. Please use the following One-Time Password (OTP) to complete verification:</p>
<p style="font-size: 1.6em; font-weight: bold; margin: 25px 0; color: #4A90E2;">{otp}</p>
<p>Enter this code on the verification page.</p>
<p>Thanks,<br>The WordHunt Team</p>
</body></html>'''
                
                if send_email(subject, email, plain_body, html_body):
                    flash('Your account is not verified. A new OTP has been sent to your email.', 'warning')
                else:
                    print(f"Failed to resend verification email to {email} during login.")
                    flash('Could not resend verification email. Please try again later or contact support.', 'danger')

                session['verification_email'] = email
                return redirect(url_for('verify_email'))
        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            user.otp = otp
            db.session.commit()
            
            subject = "WordHunt - Reset Your Password"
            plain_body = f'''You requested a password reset for WordHunt. Your One-Time Password (OTP) is: {otp}

If you didn't request this, please ignore this email.
'''
            html_body = f'''<html><body style="font-family: sans-serif;">
<p>Hi {user.username},</p>
<p>You requested a password reset for your WordHunt account. Use the following One-Time Password (OTP) to proceed:</p>
<p style="font-size: 1.6em; font-weight: bold; margin: 25px 0; color: #4A90E2;">{otp}</p>
<p>Enter this code on the password reset page.</p>
<p>If you didn't request a password reset, you can safely ignore this email.</p>
<p>Thanks,<br>The WordHunt Team</p>
</body></html>'''
            
            if send_email(subject, email, plain_body, html_body):
                 flash(f'Password reset OTP sent to {email}.', 'info')
                 session['reset_email'] = email
                 return redirect(url_for('verify_otp'))
            else:
                print(f"Failed to send password reset OTP to {email}.")
                flash('Could not send password reset email. Please try again later or contact support.', 'danger')
                return redirect(url_for('forgot_password'))
        else:
            flash('Email not found!', 'danger')
    
    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))
    
    email = session['reset_email']
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User not found or session expired.', 'danger')
        session.pop('reset_email', None)
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        action = request.form.get('action')
        otp = request.form.get('otp')
        
        if action == 'verify_otp':
            if user.otp == otp:
                session['verified_otp'] = otp
                flash('OTP Verified! Please enter your new password.', 'success')
                return render_template('verify_otp.html', otp_verified=True, verified_otp=otp)
            else:
                flash('Invalid OTP!', 'danger')
                return render_template('verify_otp.html', otp_verified=False)

        elif action == 'reset_password':
            verified_otp_from_form = request.form.get('otp')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not new_password or not confirm_password:
                flash('Please enter and confirm your new password.', 'warning')
                return render_template('verify_otp.html', otp_verified=True, verified_otp=verified_otp_from_form)
            
            if 'verified_otp' not in session:
                flash('OTP verification required. Please verify your OTP first.', 'danger')
                return redirect(url_for('verify_otp'))

            if new_password == confirm_password:
                user.password = generate_password_hash(new_password)
                user.otp = None
                db.session.commit() 
                
                session.pop('reset_email', None)
                session.pop('verified_otp', None)
                
                flash('Password reset successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Passwords do not match!', 'danger')
                return render_template('verify_otp.html', otp_verified=True, verified_otp=verified_otp_from_form)
        else:
            flash('Invalid form submission.', 'danger')
            return redirect(url_for('verify_otp'))

    if 'verified_otp' in session:
        return render_template('verify_otp.html', otp_verified=True, verified_otp=session['verified_otp'])
    
    return render_template('verify_otp.html', otp_verified=False)

@app.route('/mode')
@login_required
def mode():
    return render_template('mode.html')

@app.route('/game')
@login_required
def game_route():
    mode = request.args.get('mode', 'easy')
    grid, words = game.create_word_grid(mode)
    session['current_game_mode'] = mode # Store mode in session
    # Clear previous game score from session if any
    session.pop('last_game_score', None)
    session.pop('last_game_mode', None)
    return render_template("game.html", mode=mode, grid=grid, words=words)

@app.route('/new-grid')
@login_required
def new_grid():
    # Use mode from session if available, else default
    mode = session.get('current_game_mode', 'easy') 
    try:
        grid, words = game.create_word_grid(mode)
        return jsonify({'grid': grid, 'words': words})
    except Exception as e:
        print(f"Error generating new grid for mode {mode}: {e}")
        return jsonify({'error': 'Failed to generate new grid'}), 500

@app.route('/end-game', methods=['POST'])
@login_required
def end_game():
    try:
        data = request.get_json()
        final_score = data.get('score')
        mode = session.get('current_game_mode', 'unknown') # Get mode from session

        if final_score is None:
            return jsonify({'error': 'Missing score data'}), 400
        
        # Store score and mode in session for the score page
        session['last_game_score'] = int(final_score)
        session['last_game_mode'] = mode
        session.pop('current_game_mode', None) # Clear current game mode

        print(f"Game ended. Mode: {mode}, Score: {final_score}. Stored in session.") # Server log
        return jsonify({'message': 'Score received'}), 200
    except Exception as e:
        print(f"Error in /end-game: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/score')
@login_required
def score():
    # Get score and mode from session, not URL parameters
    score_value = session.pop('last_game_score', 0) # Pop to clear after use
    mode_value = session.pop('last_game_mode', 'easy') # Pop to clear after use
    
    if score_value == 0 and mode_value == 'easy':
        # Avoid showing score page if no score was properly submitted
        flash('No game score found in session.', 'warning')
        # Redirect to home or mode selection perhaps?
        return redirect(url_for('mode')) 

    # Calculate words found (score divided by points per word)
    points_per_word = 50 if mode_value == 'easy' else 100 if mode_value == 'normal' else 150
    words_found = 0
    if points_per_word > 0: # Avoid division by zero
         words_found = int(score_value / points_per_word)
    
    # Save score to database automatically if it's higher than the user's best score
    existing_score = Score.query.filter_by(
        user_id=current_user.id,
        mode=mode_value
    ).order_by(Score.score.desc()).first()
    
    if not existing_score or score_value > existing_score.score:
        new_score = Score(
            user_id=current_user.id,
            score=score_value,
            mode=mode_value,
            words_found=words_found
        )
        db.session.add(new_score)
        db.session.commit()
        
        flash('New high score saved!', 'success')
    
    return render_template('score.html', score=score_value, mode=mode_value, words_found=words_found)

@app.route('/leaderboard')

def leaderboard():
    modes = ['easy', 'normal', 'hard']
    leaderboards = {}

    for mode in modes:
        # Get highest score per user for the current mode
        subquery = db.session.query(
            Score.user_id,
            func.max(Score.score).label('max_score')
        ).filter(Score.mode == mode).group_by(Score.user_id).subquery()
        
        # Join with the Score and User tables
        top_scores = db.session.query(Score, User).\
            join(User, Score.user_id == User.id).\
            join(subquery, db.and_(
                Score.user_id == subquery.c.user_id,
                Score.score == subquery.c.max_score,
                Score.mode == mode  # Ensure we only get scores for the correct mode
            )).\
            order_by(Score.score.desc()).\
            limit(10).all()
            
        scores_data = [{'rank': idx+1, 'username': user.username, 'score': score.score, 
                        'words_found': score.words_found, 'date': score.date.strftime('%Y-%m-%d %H:%M')} 
                       for idx, (score, user) in enumerate(top_scores)]
        leaderboards[mode] = scores_data
        
    return render_template('leaderboard.html', leaderboards=leaderboards)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)