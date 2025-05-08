#!/usr/bin/env python3
# app.py - Flask application for the AI Companion System

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from urllib.parse import urlparse
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
# Ensure the secret key stays the same during the app's lifecycle
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = app.secret_key

# Setup the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

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

# Configure sessions - using Flask's built-in session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_USE_SIGNER'] = True

# Set remember cookie parameters (for Flask-Login)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)
app.config['REMEMBER_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True

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
    logger.debug(f"Login route called, method: {request.method}")
    logger.debug(f"Current user is authenticated: {current_user.is_authenticated}")
    
    # Already logged in
    if current_user.is_authenticated:
        logger.info("User already authenticated, redirecting to index")
        return redirect(url_for('index'))
    
    # Process login form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        # Debug info
        logger.debug(f"Login attempt for email: {email}, remember: {remember}")
        
        # Get user from database
        from models import User
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # User not found
            flash('User not found. Please check your email address.', 'error')
            logger.warning(f"Login failed - user not found: {email}")
            return render_template('login.html')
            
        # Check password
        if not user.check_password(password):
            # Password incorrect
            flash('Incorrect password. Please try again.', 'error')
            logger.warning(f"Login failed - incorrect password for: {email}")
            return render_template('login.html')
        
        # Login successful
        # First, make session permanent if remember is True
        session.permanent = True
        
        # Now login with Flask-Login (creates the session)
        login_success = login_user(user, remember=remember)
        logger.debug(f"login_user result: {login_success}")
        
        # Add custom session data
        session['user_id'] = user.id
        session['username'] = user.username
        session['login_time'] = str(datetime.now())
        session.modified = True
        
        # Log success
        flash('Login successful!', 'success')
        logger.info(f"User logged in successfully: {email}")
        logger.debug(f"Session data: {dict(session)}")
        logger.debug(f"User ID in session: {session.get('user_id')}")
        
        # Get the page the user was trying to access
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
            
        logger.debug(f"Redirecting to: {next_page}")
        return redirect(next_page)
    
    # Show login form
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
    logger.debug(f"Index page accessed. User authenticated: {current_user.is_authenticated}")
    logger.debug(f"Current user: {current_user.username if current_user.is_authenticated else 'None'}")
    logger.debug(f"Session data: {dict(session)}")
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
    
@app.route('/check_auth')
def check_auth():
    """Diagnostic endpoint to check authentication status."""
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user_id": current_user.id,
            "username": current_user.username,
            "session_data": dict(session),
            "remember_cookie": request.cookies.get('remember_token') is not None
        })
    return jsonify({
        "authenticated": False,
        "session_exists": bool(session),
        "session_keys": list(session.keys()) if session else []
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
