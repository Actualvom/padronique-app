import os
import logging
import yaml
from flask import Flask, render_template, request, jsonify
from swift_app.bridging_api.api import api_bp
from core.main_controller import initialize_padronique

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "padronique_default_secret")

# Register API blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# Load config
def load_config():
    try:
        with open("config/settings.yaml", 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

config = load_config()

# Initialize Padronique in background
padronique_instance = initialize_padronique()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/memory')
def memory():
    memories = padronique_instance.soul.get_memory_overview() if padronique_instance and padronique_instance.soul else []
    return render_template('memory.html', memories=memories)

@app.route('/settings')
def settings():
    return render_template('settings.html', config=config)

@app.route('/interact', methods=['POST'])
def interact():
    data = request.json
    user_input = data.get('input', '')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    try:
        if padronique_instance and padronique_instance.orchestrator:
            response = padronique_instance.orchestrator.process_user_input(user_input)
            return jsonify({'response': response})
        else:
            return jsonify({'error': 'Padronique system not initialized yet'}), 503
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
