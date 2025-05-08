#!/usr/bin/env python3
# app.py - Flask application for the AI Companion System

import os
import logging
from flask import Flask, render_template, request, jsonify
from api.routes import register_api_routes
from utils.logger import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

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
