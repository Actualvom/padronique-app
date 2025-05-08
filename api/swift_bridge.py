#!/usr/bin/env python3
# api/swift_bridge.py - Swift bridge for mobile integration

import logging
import time
import json
import uuid
from typing import Dict, Any, List, Optional

from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

# Create Swift bridge blueprint
swift_bp = Blueprint('swift_bridge', __name__, url_prefix='/api/swift')

def register_swift_routes(app):
    """Register Swift bridge routes with the Flask app."""
    if app.config.get('ORCHESTRATOR', {}).config.get('api', {}).get('swift_bridge_enabled', False):
        app.register_blueprint(swift_bp)
        logger.info("Swift bridge API routes registered")
    else:
        logger.info("Swift bridge API disabled in configuration")


class SwiftBridge:
    """
    Swift bridge for mobile integration with the AI Companion System.
    
    Provides a simplified API for Swift-based mobile apps to interact with the system.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize the SwiftBridge.
        
        Args:
            orchestrator: The system orchestrator
        """
        self.orchestrator = orchestrator
        self.active_sessions = {}
        self.session_timeout = 3600  # 1 hour
        logger.info("Swift bridge initialized")
    
    def create_session(self, device_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new session for a mobile device.
        
        Args:
            device_id: Unique identifier for the device
            user_info: Information about the user
            
        Returns:
            Session information
        """
        session_id = str(uuid.uuid4())
        
        session = {
            'id': session_id,
            'device_id': device_id,
            'user_info': user_info,
            'created': time.time(),
            'last_activity': time.time(),
            'message_count': 0
        }
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Created new Swift session {session_id} for device {device_id}")
        return {
            'session_id': session_id,
            'created': session['created'],
            'status': 'active'
        }
    
    def process_message(self, session_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message from a mobile device.
        
        Args:
            session_id: ID of the session
            message: Message to process
            
        Returns:
            Response message
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Invalid session ID: {session_id}")
            return {
                'error': 'Invalid session ID',
                'status': 'error'
            }
        
        # Update session activity
        session = self.active_sessions[session_id]
        session['last_activity'] = time.time()
        session['message_count'] += 1
        
        # Process the message
        try:
            # Format input for the orchestrator
            input_data = {
                'type': message.get('type', 'text'),
                'content': message.get('content', ''),
                'source': 'swift',
                'session_id': session_id,
                'device_id': session['device_id'],
                'auth_token': message.get('auth_token')
            }
            
            # Add any additional context from the session
            if 'context' in message:
                input_data['context'] = message['context']
            
            # Process through orchestrator
            response = self.orchestrator.process_input(input_data)
            
            # Format response for Swift
            swift_response = {
                'id': str(uuid.uuid4()),
                'timestamp': time.time(),
                'content': response.get('response', ''),
                'status': 'ok',
                'type': response.get('type', 'text')
            }
            
            # Add memory ID if available for reference
            if 'memory_id' in response:
                swift_response['memory_id'] = response['memory_id']
            
            return swift_response
            
        except Exception as e:
            logger.error(f"Error processing Swift message: {e}")
            return {
                'error': str(e),
                'status': 'error',
                'timestamp': time.time()
            }
    
    def end_session(self, session_id: str) -> bool:
        """
        End a session.
        
        Args:
            session_id: ID of the session to end
            
        Returns:
            True if successful, False otherwise
        """
        if session_id in self.active_sessions:
            # Save session data to memory
            session = self.active_sessions[session_id]
            
            try:
                self.orchestrator.memory_manager.store_memory({
                    'type': 'swift_session',
                    'session_id': session_id,
                    'device_id': session['device_id'],
                    'user_info': session['user_info'],
                    'created': session['created'],
                    'ended': time.time(),
                    'message_count': session['message_count']
                }, tags=['swift', 'session'])
            except Exception as e:
                logger.error(f"Error storing session data: {e}")
            
            # Remove session
            del self.active_sessions[session_id]
            logger.info(f"Ended Swift session {session_id}")
            return True
        
        logger.warning(f"Attempted to end nonexistent session: {session_id}")
        return False
    
    def cleanup_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired Swift sessions")
        return len(expired_sessions)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get information about all active sessions.
        
        Returns:
            List of active session information
        """
        sessions = []
        
        for session_id, session in self.active_sessions.items():
            sessions.append({
                'session_id': session_id,
                'device_id': session['device_id'],
                'created': session['created'],
                'last_activity': session['last_activity'],
                'message_count': session['message_count']
            })
        
        return sessions


# Swift bridge API routes

@swift_bp.route('/session', methods=['POST'])
def create_session():
    """Create a new Swift session."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    # Initialize bridge if not already in app config
    if 'SWIFT_BRIDGE' not in current_app.config:
        current_app.config['SWIFT_BRIDGE'] = SwiftBridge(orchestrator)
    
    bridge = current_app.config['SWIFT_BRIDGE']
    
    try:
        data = request.json
        
        if not data or 'device_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Device ID is required'
            }), 400
        
        device_id = data['device_id']
        user_info = data.get('user_info', {})
        
        session = bridge.create_session(device_id, user_info)
        
        return jsonify({
            'status': 'ok',
            'session': session
        })
    
    except Exception as e:
        logger.error(f"Error creating Swift session: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error creating session: {str(e)}'
        }), 500


@swift_bp.route('/message', methods=['POST'])
def process_message():
    """Process a message from a Swift client."""
    if 'SWIFT_BRIDGE' not in current_app.config:
        return jsonify({
            'status': 'error',
            'message': 'Swift bridge not initialized'
        }), 500
    
    bridge = current_app.config['SWIFT_BRIDGE']
    
    try:
        data = request.json
        
        if not data or 'session_id' not in data or 'message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Session ID and message are required'
            }), 400
        
        session_id = data['session_id']
        message = data['message']
        
        response = bridge.process_message(session_id, message)
        
        if 'error' in response and response.get('status') == 'error':
            return jsonify({
                'status': 'error',
                'message': response['error'],
                'response': response
            }), 400
        
        return jsonify({
            'status': 'ok',
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Error processing Swift message: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing message: {str(e)}'
        }), 500


@swift_bp.route('/session/<session_id>', methods=['DELETE'])
def end_session(session_id):
    """End a Swift session."""
    if 'SWIFT_BRIDGE' not in current_app.config:
        return jsonify({
            'status': 'error',
            'message': 'Swift bridge not initialized'
        }), 500
    
    bridge = current_app.config['SWIFT_BRIDGE']
    
    try:
        result = bridge.end_session(session_id)
        
        if result:
            return jsonify({
                'status': 'ok',
                'message': f'Session {session_id} ended successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Session {session_id} not found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error ending Swift session: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error ending session: {str(e)}'
        }), 500


@swift_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get information about all active Swift sessions."""
    if 'SWIFT_BRIDGE' not in current_app.config:
        return jsonify({
            'status': 'error',
            'message': 'Swift bridge not initialized'
        }), 500
    
    bridge = current_app.config['SWIFT_BRIDGE']
    
    try:
        # Cleanup expired sessions
        bridge.cleanup_sessions()
        
        # Get active sessions
        sessions = bridge.get_active_sessions()
        
        return jsonify({
            'status': 'ok',
            'count': len(sessions),
            'sessions': sessions
        })
    
    except Exception as e:
        logger.error(f"Error retrieving Swift sessions: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving sessions: {str(e)}'
        }), 500


@swift_bp.route('/ping', methods=['GET'])
def ping():
    """Simple endpoint to check if Swift bridge is available."""
    return jsonify({
        'status': 'ok',
        'message': 'Swift bridge is available',
        'timestamp': time.time()
    })
