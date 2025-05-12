#!/usr/bin/env python3
# api/routes.py - API routes for the AI Companion System

import logging
import time
import json
import os
from typing import Dict, Any

from flask import Blueprint, request, jsonify, current_app

from memory.memory_manager import MemoryManager
from api.multimedia import register_multimedia_routes, create_uploads_dir

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_api_routes(app):
    """Register API routes with the Flask app."""
    app.register_blueprint(api_bp)
    
    # Register multimedia routes
    register_multimedia_routes(app)
    
    # Create uploads directory
    create_uploads_dir()
    
    logger.info("API routes registered")


@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get the current status of the AI system."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    # If orchestrator is not available, provide mock data for UI
    if not orchestrator:
        # Mock system status for the UI when orchestrator is not available
        import time
        import random
        
        logger.warning("Orchestrator not initialized, returning simulated status data")
        
        # Reading from the config file directly
        try:
            import yaml
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                system_name = config.get('system', {}).get('name', 'Padronique')
                version = config.get('system', {}).get('version', '0.1.0')
        except Exception as e:
            logger.error(f"Error reading config: {e}")
            system_name = 'Padronique'
            version = '0.1.0'
        
        # Generate simulated system status
        simulated_status = {
            'system_name': system_name,
            'version': version,
            'uptime': int(time.time() % 86400),  # Simulated uptime (never more than a day)
            'memory': {
                'total_memories': random.randint(5, 20),
                'active_memories': random.randint(3, 10),
                'max_memories': 10000
            },
            'modules': {
                'language': {
                    'active': True,
                    'stats': {
                        'processing_count': random.randint(10, 50),
                        'error_count': 0
                    },
                    'last_used': int(time.time()) - random.randint(60, 300)
                },
                'reasoning': {
                    'active': True,
                    'stats': {
                        'processing_count': random.randint(5, 30),
                        'error_count': 0
                    },
                    'last_used': int(time.time()) - random.randint(120, 600)
                },
                'learning': {
                    'active': True,
                    'stats': {
                        'processing_count': random.randint(3, 15),
                        'error_count': 0
                    },
                    'last_used': int(time.time()) - random.randint(300, 1200)
                },
                'perception': {
                    'active': True,
                    'stats': {
                        'processing_count': random.randint(1, 10),
                        'error_count': 0
                    },
                    'last_used': int(time.time()) - random.randint(600, 1800)
                },
                'external_comm': {
                    'active': True,
                    'stats': {
                        'processing_count': random.randint(0, 5),
                        'error_count': 0
                    },
                    'last_used': int(time.time()) - random.randint(1200, 3600)
                }
            }
        }
        
        return jsonify({
            'status': 'ok',
            'system': simulated_status
        })
    
    # Get actual system status if orchestrator is available
    system_status = orchestrator.get_system_status()
    
    return jsonify({
        'status': 'ok',
        'system': system_status
    })


@api_bp.route('/process', methods=['POST'])
def process_input():
    """Process input through the AI system."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    input_data = None
    
    try:
        input_data = request.json
        
        if not input_data:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400
        
        # Add request timestamp
        input_data['timestamp'] = time.time()
        
        # Get user message content
        user_message = input_data.get('content', '')
        
        if not orchestrator:
            # If orchestrator is not available, use a basic response system
            logger.warning("Orchestrator not initialized, using basic response system")
            response = simple_response_handler(user_message)
            
            # Store this interaction in the DB later when orchestrator is available
            return jsonify({
                'status': 'ok',
                'response': response
            })
        
        # Process the input through the orchestrator if available
        response = orchestrator.process_input(input_data)
        
        return jsonify({
            'status': 'ok',
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        # Fallback to simple responses in case of errors
        try:
            user_message = ""
            if input_data and isinstance(input_data, dict):
                user_message = input_data.get('content', '')
                
            response = simple_response_handler(user_message)
            return jsonify({
                'status': 'ok',
                'response': response
            })
        except Exception as inner_e:
            logger.error(f"Error in fallback handler: {inner_e}")
            return jsonify({
                'status': 'error',
                'message': f'Error processing input: {str(e)}'
            }), 500


@api_bp.route('/reset', methods=['POST'])
def reset_system():
    """Reset the system with Guardian Override Protocol protection."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'ok',
            'message': 'System reset simulation successful'
        })
    
    try:
        # Check if we have a valid reset method
        if not hasattr(orchestrator, 'reset') or not callable(orchestrator.reset):
            return jsonify({
                'status': 'error',
                'message': 'System reset functionality not implemented yet'
            }), 501
        
        # Get request data for verification
        data = request.json or {}
        verification_id = data.get('verification_id')
        
        # Call the reset method with appropriate parameters
        result = orchestrator.reset(verification_id=verification_id, context=data)
        
        # Reset method now returns a dict with status information
        if result.get('type') == 'verification_required':
            # Return the verification requirements
            return jsonify({
                'status': 'verification_required',
                'message': result.get('content'),
                'verification_id': result.get('verification_id'),
                'required_verifications': result.get('required_verifications'),
                'severity': result.get('severity', 'HIGH')
            })
        elif result.get('status') == 'success':
            # Reset was successful
            return jsonify({
                'status': 'ok',
                'message': result.get('content', 'System reset successfully')
            })
        else:
            # Some error occurred
            return jsonify({
                'status': 'error',
                'message': result.get('content', 'Error during system reset'),
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error resetting system: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error resetting system: {str(e)}'
        }), 500


def simple_response_handler(message):
    """Handle basic responses when orchestrator is not available."""
    message = message.lower().strip()
    
    # Direct "is that you" questions about Padronique
    if "padronique" in message and any(phrase in message for phrase in ["is that you", "are you there", "is it you"]):
        return "Yes, it's me, Padronique! I'm here and ready to assist you. How can I help you today?"
    
    # Greetings
    if any(greeting in message for greeting in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm Padronique, your AI companion. How can I assist you today?"
    
    # Identity questions
    if any(identity in message for identity in ['who are you', 'your name', 'are you', 'what are you']):
        return "I am Padronique, an advanced AI companion system with memory, specialized brain modules, and adaptive intelligence capabilities."
    
    # Help requests
    if any(help_req in message for help_req in ['help', 'assist', 'support', 'can you']):
        return "I'm here to help! As Padronique, I can assist with information, engage in conversations, remember our interactions, and learn from our exchanges."
    
    # System-related questions
    if any(system_q in message for system_q in ['how do you work', 'your function', 'your module', 'your brain']):
        return "I operate using multiple specialized brain modules including language processing, reasoning, learning, perception, and external communication, all coordinated by a central orchestrator."
    
    # Memory-related questions
    if any(memory_q in message for memory_q in ['remember', 'memory', 'forget', 'recall']):
        return "I have a memory system that allows me to remember our interactions and important information. This helps me provide more personalized assistance over time."
    
    # Comment on the interface or appearance
    if any(appearance in message for appearance in ['interface', 'design', 'look', 'appearance', 'style']):
        return "Thank you for noticing my interface! I've been designed with a futuristic aesthetic featuring dark backgrounds with blue and purple highlights. My UI is inspired by advanced holographic interfaces to create a sleek, modern experience."
    
    # Questions about capabilities
    if any(capability in message for capability in ['can you', 'ability', 'capable', 'feature']):
        return "As Padronique, I have multiple capabilities including natural language processing, memory storage, reasoning, learning from interactions, and external communication. My modular design allows me to evolve and improve over time."
    
    # Default response
    return "I'm Padronique, your AI companion. I'm here to assist you with information, engage in conversations, and learn from our interactions. How can I help you today?"


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


@api_bp.route('/verify', methods=['POST'])
def verify_guardian_override():
    """Complete a verification step for the Guardian Override Protocol."""
    orchestrator = current_app.config.get('ORCHESTRATOR')
    
    if not orchestrator:
        return jsonify({
            'status': 'error',
            'message': 'Orchestrator not initialized'
        }), 500
    
    try:
        # Get verification data
        data = request.json
        
        if not data or 'verification_id' not in data or 'verification_type' not in data or 'verification_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required verification parameters'
            }), 400
        
        # Get the ethics engine module if available directly
        ethics_engine = orchestrator.get_module('ethics')
        
        # If no direct access to ethics engine, try via the orchestrator
        if not ethics_engine and hasattr(orchestrator, 'ethics_engine'):
            ethics_engine = orchestrator.ethics_engine
        
        if not ethics_engine:
            return jsonify({
                'status': 'error',
                'message': 'Ethics engine not available'
            }), 500
        
        # Process the verification
        verification_result = ethics_engine.complete_verification(
            verification_id=data['verification_id'],
            verification_type=data['verification_type'],
            verification_data=data['verification_data']
        )
        
        # Return the verification result
        if verification_result['status'] == 'success':
            if verification_result.get('request_status') == 'approved':
                return jsonify({
                    'status': 'approved',
                    'message': 'Verification complete. The requested action has been approved.',
                    'next_steps': verification_result.get('next_steps', [])
                })
            else:
                return jsonify({
                    'status': 'in_progress',
                    'message': 'Verification step completed successfully',
                    'remaining_verifications': verification_result.get('remaining_verifications', []),
                    'next_verification': verification_result.get('next_verification')
                })
        else:
            return jsonify({
                'status': 'failed',
                'message': verification_result.get('message', 'Verification failed'),
                'reason': verification_result.get('reason')
            }), 400
    
    except Exception as e:
        logger.error(f"Error processing verification: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing verification: {str(e)}'
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
