#!/usr/bin/env python3
# app.py - Flask application for the AI Companion System

import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from api.routes import register_api_routes
from utils.logger import setup_logging

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

# Create database tables
with app.app_context():
    # Import models to register them with SQLAlchemy
    import models
    db.create_all()

# In production, set this to a secure value
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Create an orchestrator instance but don't initialize yet
# This will be initialized in main.py
app.config['ORCHESTRATOR'] = None

# Enable better debugging
if app.debug:
    app.config['TEMPLATES_AUTO_RELOAD'] = True

# Register API routes
register_api_routes(app)

@app.route('/')
def index():
    """Render the main interface."""
    return render_template('index.html')

@app.route('/dashboard')
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
