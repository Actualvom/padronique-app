#!/usr/bin/env python3
# api/routes.py - API routes for the AI Companion System

import logging
import time
import json
from typing import Dict, Any

from flask import Blueprint, request, jsonify, current_app

from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_api_routes(app):
    """Register API routes with the Flask app."""
    app.register_blueprint(api_bp)
    logger.info("API routes registered")


@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get the current status of the AI system."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    system_status = orchestrator.get_system_status()
    
    return jsonify({
        'status': 'ok',
        'system': system_status
    })


@api_bp.route('/process', methods=['POST'])
def process_input():
    """Process input through the AI system."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        input_data = request.json
        
        if not input_data:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400
        
        # Add request timestamp
        input_data['timestamp'] = time.time()
        
        # Process the input
        response = orchestrator.process_input(input_data)
        
        return jsonify({
            'status': 'ok',
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing input: {str(e)}'
        }), 500


@api_bp.route('/memory', methods=['GET'])
def get_memories():
    """Retrieve memories based on query parameters."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        memory_manager = orchestrator.memory_manager
        
        # Get query parameters
        query = request.args.get('query', '')
        tags = request.args.get('tags', '')
        limit = int(request.args.get('limit', 10))
        
        # Convert tags string to list
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        # Search memories
        if query:
            memories = memory_manager.search_memories(query, tag_list, limit)
        elif tag_list:
            memories = memory_manager.get_memories_by_tags(tag_list, limit)
        else:
            memories = memory_manager.get_recent_memories(limit)
        
        return jsonify({
            'status': 'ok',
            'count': len(memories),
            'memories': memories
        })
    
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving memories: {str(e)}'
        }), 500


@api_bp.route('/memory/<memory_id>', methods=['GET'])
def get_memory(memory_id):
    """Retrieve a specific memory by ID."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        memory_manager = orchestrator.memory_manager
        memory = memory_manager.retrieve_memory(memory_id)
        
        if memory:
            return jsonify({
                'status': 'ok',
                'memory': memory
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Memory with ID {memory_id} not found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error retrieving memory {memory_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving memory: {str(e)}'
        }), 500


@api_bp.route('/memory/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """Delete a specific memory by ID."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        memory_manager = orchestrator.memory_manager
        result = memory_manager.delete_memory(memory_id)
        
        if result:
            return jsonify({
                'status': 'ok',
                'message': f'Memory {memory_id} deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Memory with ID {memory_id} not found or could not be deleted'
            }), 404
    
    except Exception as e:
        logger.error(f"Error deleting memory {memory_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error deleting memory: {str(e)}'
        }), 500


@api_bp.route('/memory', methods=['POST'])
def create_memory():
    """Create a new memory."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        memory_manager = orchestrator.memory_manager
        data = request.json
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No memory data provided'
            }), 400
        
        # Extract tags if provided
        tags = data.pop('tags', [])
        
        # Store the memory
        memory_id = memory_manager.store_memory(data, tags)
        
        return jsonify({
            'status': 'ok',
            'memory_id': memory_id,
            'message': 'Memory created successfully'
        })
    
    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error creating memory: {str(e)}'
        }), 500


@api_bp.route('/memory/<memory_id>/tags', methods=['POST'])
def add_tags(memory_id):
    """Add tags to a memory."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        memory_manager = orchestrator.memory_manager
        data = request.json
        
        if not data or 'tags' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No tags provided'
            }), 400
        
        tags = data['tags']
        result = memory_manager.add_tags_to_memory(memory_id, tags)
        
        if result:
            return jsonify({
                'status': 'ok',
                'message': f'Tags added to memory {memory_id}'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Memory with ID {memory_id} not found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error adding tags to memory {memory_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error adding tags: {str(e)}'
        }), 500


@api_bp.route('/feedback', methods=['POST'])
def provide_feedback():
    """Provide feedback for learning."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        learning_module = orchestrator.get_module('learning')
        
        if not learning_module:
            return jsonify({
                'status': 'error',
                'message': 'Learning module not available'
            }), 500
        
        data = request.json
        
        if not data or 'interaction_id' not in data or 'feedback' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required feedback data'
            }), 400
        
        interaction_id = data['interaction_id']
        feedback = data['feedback']
        
        result = learning_module.provide_feedback(interaction_id, feedback)
        
        if result:
            return jsonify({
                'status': 'ok',
                'message': 'Feedback processed successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to process feedback'
            }), 500
    
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing feedback: {str(e)}'
        }), 500


@api_bp.route('/modules', methods=['GET'])
def get_modules():
    """Get information about all brain modules."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    modules_info = {}
    for name, module in orchestrator.modules.items():
        modules_info[name] = {
            'active': module.is_active(),
            'stats': module.get_stats()
        }
    
    return jsonify({
        'status': 'ok',
        'modules': modules_info
    })


@api_bp.route('/modules/<module_name>', methods=['GET'])
def get_module_info(module_name):
    """Get information about a specific brain module."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    module = orchestrator.get_module(module_name)
    
    if not module:
        return jsonify({
            'status': 'error',
            'message': f'Module {module_name} not found'
        }), 404
    
    module_info = {
        'active': module.is_active(),
        'stats': module.get_stats(),
        'config': module.config
    }
    
    return jsonify({
        'status': 'ok',
        'module': module_info
    })


@api_bp.route('/modules/<module_name>/toggle', methods=['POST'])
def toggle_module(module_name):
    """Toggle a brain module's active state."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    module = orchestrator.get_module(module_name)
    
    if not module:
        return jsonify({
            'status': 'error',
            'message': f'Module {module_name} not found'
        }), 404
    
    data = request.json or {}
    active = data.get('active')
    
    if active is None:
        # Toggle current state
        active = not module.is_active()
    
    if active:
        module.activate()
    else:
        module.deactivate()
    
    return jsonify({
        'status': 'ok',
        'module': module_name,
        'active': module.is_active()
    })


@api_bp.route('/modules/<module_name>/config', methods=['PATCH'])
def update_module_config(module_name):
    """Update a brain module's configuration."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    module = orchestrator.get_module(module_name)
    
    if not module:
        return jsonify({
            'status': 'error',
            'message': f'Module {module_name} not found'
        }), 404
    
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No configuration data provided'
        }), 400
    
    module.update_config(data)
    
    return jsonify({
        'status': 'ok',
        'module': module_name,
        'config': module.config
    })


@api_bp.route('/sandbox/test', methods=['POST'])
def test_in_sandbox():
    """Test code or module in the sandbox environment."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    from sandbox.module_tester import SandboxTester
    
    try:
        data = request.json
        
        if not data or 'code' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No code provided for testing'
            }), 400
        
        sandbox_config = orchestrator.config.get('sandbox', {})
        tester = SandboxTester(sandbox_config)
        
        result = tester.test_code(data['code'], data.get('inputs', {}))
        
        return jsonify({
            'status': 'ok',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Error in sandbox testing: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Sandbox testing error: {str(e)}'
        }), 500
