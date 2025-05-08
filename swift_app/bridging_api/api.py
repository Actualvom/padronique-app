from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__)

@api_bp.route('/ping', methods=['GET'])
def ping():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "API is operational"})

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Process a chat message and return a response."""
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    # In a real implementation, this would process the message through Padronique
    # For now, just echo the message back
    return jsonify({
        "response": f"Echo: {data['message']}",
        "timestamp": "2025-05-08T18:42:01Z"  # Static timestamp for testing
    })