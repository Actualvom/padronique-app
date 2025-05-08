#!/usr/bin/env python3
# app.py - Flask application for the AI Companion System

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session
from sqlalchemy.orm import DeclarativeBase
from api.routes import register_api_routes
from utils.logger import setup_logging
from werkzeug.security import generate_password_hash

# Create a base class for SQLAlchemy models to use
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the custom base class
db = SQLAlchemy(model_class=Base)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Setup the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access Padronique.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    # Import models to register them with SQLAlchemy
    import models
    db.create_all()
    
    # Create default user if it doesn't exist
    try:
        default_user = models.User.query.filter_by(email='jordyfshears@gmail.com').first()
        if not default_user:
            # Create a new user object
            default_user = models.User()
            default_user.username = 'Jordan'
            default_user.email = 'jordyfshears@gmail.com'
            default_user.set_password('Pterodactyl1ke$ha')
            db.session.add(default_user)
            db.session.flush()  # Flush to get the ID
            
            # Create default settings for the user
            user_settings = models.UserSettings()
            user_settings.user_id = default_user.id
            db.session.add(user_settings)
            
            db.session.commit()
            logger.info("Created default user account")
    except Exception as e:
        logger.error(f"Error creating default user: {e}")

# Session configuration
import tempfile
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_USE_SIGNER'] = True

# Initialize Flask-Session
Session(app)

# Create an orchestrator instance but don't initialize yet
# This will be initialized in main.py
app.config['ORCHESTRATOR'] = None

# Enable better debugging
if app.debug:
    app.config['TEMPLATES_AUTO_RELOAD'] = True

# Register API routes
register_api_routes(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        from models import User
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # User not found
            flash('User not found. Please check your email address.', 'error')
            logger.warning(f"Login attempt failed - user not found: {email}")
        elif not user.check_password(password):
            # Password incorrect
            flash('Incorrect password. Please try again.', 'error')
            logger.warning(f"Login attempt failed - incorrect password for user: {email}")
        else:
            # Login successful
            login_user(user, remember=remember)
            
            # Set additional information in session
            session['user_id'] = user.id
            session['username'] = user.username
            session.modified = True  # Ensure session is saved
            
            flash('Login successful!', 'success')
            logger.info(f"User logged in successfully: {email}")
            
            # Debug session
            logger.debug(f"Session after login: {session}")
            
            # Redirect to requested page or default to index
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Render the main interface."""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard interface."""
    return render_template('dashboard.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
