"""
API routes for multimedia processing including voice, images, files, and web search
"""

import os
import json
import logging
import base64
import tempfile
import uuid
from datetime import datetime
from flask import request, jsonify, current_app
import requests
from werkzeug.utils import secure_filename
from utils.web_scraper import get_website_text_content

# Initialize logging
logger = logging.getLogger(__name__)

def register_multimedia_routes(app):
    """Register multimedia processing routes with the Flask app."""
    
    @app.route('/api/transcribe', methods=['POST'])
    def transcribe_audio():
        """Transcribe audio to text using OpenAI."""
        # Initialize temp_path to None to prevent unbound variable error
        temp_path = None
        
        logger.info("Transcribe audio API endpoint called")
        
        if 'audio' not in request.files:
            logger.warning("No audio file provided in request")
            return jsonify({"status": "error", "message": "No audio file provided"}), 400
            
        audio_file = request.files['audio']
        logger.info(f"Received audio file: {audio_file.filename}, content type: {audio_file.content_type}")
        
        if not audio_file.filename:
            logger.warning("Empty filename received")
            return jsonify({"status": "error", "message": "No audio file selected"}), 400
            
        # Create a temporary file to store the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_path = temp_file.name
        audio_file.save(temp_path)
        temp_file.close()
        
        # Log file details
        file_size = os.path.getsize(temp_path)
        logger.info(f"Audio saved to temporary file: {temp_path}, size: {file_size} bytes")
        
        try:
            # Check for OpenAI API key
            if not os.environ.get("OPENAI_API_KEY"):
                logger.error("OPENAI_API_KEY environment variable is not set")
                return jsonify({"status": "error", "message": "OpenAI API key not configured"}), 500
            
            # Get the orchestrator from the app config
            logger.info("Retrieving orchestrator from app config")
            orchestrator = current_app.config.get('ORCHESTRATOR')
            
            if orchestrator and orchestrator.llm_service:
                logger.info("Using orchestrator for transcription")
                
                # Use the voice module if available
                if orchestrator.voice_module:
                    logger.info("Using voice module for transcription")
                    transcription = orchestrator.voice_module.transcribe_audio(temp_path)
                else:
                    # Fallback to direct LLM service
                    logger.info("Voice module not available, using LLM service directly")
                    transcription = orchestrator.llm_service.transcribe_audio(temp_path)
                
                logger.info(f"Transcription successful, text length: {len(transcription)}")
                return jsonify({
                    "status": "ok",
                    "text": transcription
                })
            else:
                # Fallback using OpenAI directly if orchestrator is not available
                logger.info("Orchestrator not available, using OpenAI directly")
                from openai import OpenAI
                
                logger.info("Initializing OpenAI client")
                openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                
                logger.info("Sending audio file to OpenAI for transcription")
                with open(temp_path, "rb") as audio_file:
                    try:
                        response = openai_client.audio.transcriptions.create(
                            model="whisper-1", 
                            file=audio_file
                        )
                        logger.info(f"OpenAI transcription successful, text length: {len(response.text)}")
                    except Exception as e:
                        logger.error(f"OpenAI transcription failed: {e}")
                        raise
                
                return jsonify({
                    "status": "ok",
                    "text": response.text
                })
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            logger.exception("Detailed transcription error:")
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            # Clean up the temporary file
            try:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    logger.info(f"Temporary file {temp_path} deleted")
            except Exception as e:
                logger.error(f"Error removing temporary file: {e}")
    
    @app.route('/api/process-image', methods=['POST'])
    def process_image():
        """Process and analyze an image."""
        # Initialize temp_path to None to prevent unbound variable error
        temp_path = None
        
        if 'image' not in request.files:
            logger.warning("No image file provided in request")
            return jsonify({"status": "error", "message": "No image file provided"}), 400
            
        image_file = request.files['image']
        logger.info(f"Received image file: {image_file.filename}, content type: {image_file.content_type}")
        
        if not image_file.filename:
            logger.warning("Empty filename received")
            return jsonify({"status": "error", "message": "No image file selected"}), 400
            
        # Validate file type
        filename = secure_filename(image_file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        logger.info(f"Image file extension: {file_ext}")
        
        if file_ext not in ['jpg', 'jpeg', 'png', 'gif']:
            logger.warning(f"Unsupported file format: {file_ext}")
            return jsonify({"status": "error", "message": "Unsupported file format"}), 400
            
        try:
            # Save the image temporarily
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}')
            temp_path = temp_file.name
            image_file.save(temp_path)
            temp_file.close()
            
            file_size = os.path.getsize(temp_path)
            logger.info(f"Image saved to temporary file: {temp_path}, size: {file_size} bytes")
            
            # Get the orchestrator from the app config
            logger.info("Retrieving orchestrator from app config")
            orchestrator = current_app.config.get('ORCHESTRATOR')
            
            # Convert image to base64 for API processing
            logger.info("Converting image to base64")
            with open(temp_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Generate a unique filename for serving the image
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            save_path = os.path.join('static', 'uploads', unique_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            logger.info(f"Created unique filename: {unique_filename}")
            
            # Copy the temp file to the uploads directory
            logger.info(f"Copying file to uploads directory: {save_path}")
            with open(temp_path, "rb") as src, open(save_path, "wb") as dst:
                dst.write(src.read())
            
            # Generate public URL
            image_url = f"/static/uploads/{unique_filename}"
            logger.info(f"Generated public URL: {image_url}")
            
            # Analyze the image
            analysis = "Image uploaded successfully. Please describe what you see in this image."
            
            if orchestrator and orchestrator.llm_service:
                try:
                    logger.info("Using LLM service to analyze image")
                    # Use LLM service to analyze image
                    analysis = orchestrator.llm_service.analyze_image(base64_image)
                    logger.info("Image analysis completed successfully")
                except Exception as analysis_err:
                    logger.error(f"Error analyzing image: {analysis_err}")
                    # Fallback message if analysis fails
                    analysis = "I received your image but wasn't able to analyze it. How would you like me to help with this image?"
            else:
                logger.info("Orchestrator or LLM service not available, using default analysis message")
            
            return jsonify({
                "status": "ok",
                "image_url": image_url,
                "analysis": analysis
            })
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            logger.exception("Detailed image processing error:")
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            # Clean up the temporary file
            try:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    logger.info(f"Temporary file {temp_path} deleted")
            except Exception as e:
                logger.error(f"Error removing temporary file: {e}")
    
    @app.route('/api/process-file', methods=['POST'])
    def process_file():
        """Process uploaded files."""
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({"status": "error", "message": "No file selected"}), 400
            
        # Validate and secure filename
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        # Handle different file types
        if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            # Images
            return process_image_file(file, filename, file_ext)
        elif file_ext in ['txt']:
            # Text files
            return process_text_file(file)
        elif file_ext in ['pdf', 'doc', 'docx']:
            # Documents
            return process_document_file(file, filename, file_ext)
        else:
            # Unsupported files
            return jsonify({
                "status": "error", 
                "message": f"Unsupported file format: {file_ext}"
            }), 400
    
    def process_image_file(file, filename, file_ext):
        """Process image files."""
        try:
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            save_path = os.path.join('static', 'uploads', unique_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save the file
            file.save(save_path)
            
            # Generate URL for frontend
            file_url = f"/static/uploads/{unique_filename}"
            
            return jsonify({
                "status": "ok",
                "type": "image",
                "url": file_url
            })
        except Exception as e:
            logger.error(f"Error processing image file: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def process_text_file(file):
        """Process text files."""
        try:
            content = file.read().decode('utf-8')
            
            return jsonify({
                "status": "ok",
                "type": "text",
                "content": content
            })
        except UnicodeDecodeError:
            try:
                # Try different encoding
                file.seek(0)
                content = file.read().decode('latin-1')
                
                return jsonify({
                    "status": "ok",
                    "type": "text",
                    "content": content
                })
            except Exception as e:
                logger.error(f"Error decoding text file: {e}")
                return jsonify({"status": "error", "message": "Could not decode text file"}), 500
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def process_document_file(file, filename, file_ext):
        """Process document files (placeholder - would need document parsing libraries)."""
        try:
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            save_path = os.path.join('static', 'uploads', unique_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save the file
            file.save(save_path)
            
            # Generate URL for frontend
            file_url = f"/static/uploads/{unique_filename}"
            
            return jsonify({
                "status": "ok",
                "type": "document",
                "url": file_url,
                "message": "Document uploaded successfully. Please note that document parsing is limited."
            })
        except Exception as e:
            logger.error(f"Error processing document file: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route('/api/web-search', methods=['GET'])
    def web_search():
        """Perform a web search and return results."""
        query = request.args.get('query', '')
        
        if not query:
            return jsonify({"status": "error", "message": "No search query provided"}), 400
            
        try:
            # Use the web scraper to get content from relevant URLs
            # This is a simplified implementation
            search_results = []
            
            # In a real implementation, you would use a search API
            # For demonstration, we'll use a placeholder approach with web scraping
            # This would typically use Google Custom Search API or similar
            
            # Mock search results (in a real app, you'd integrate with a search API)
            search_results = [
                {
                    "title": f"Search results for: {query}",
                    "url": f"https://example.com/search?q={query}",
                    "snippet": "To perform actual web searches, you would need to integrate with a search API such as Google Custom Search, Bing Search, or similar services. This would require API keys and proper configuration."
                },
                {
                    "title": "Web Search Integration",
                    "url": "https://example.com/integration",
                    "snippet": "For a production implementation, consider integrating with a search API and implementing proper caching, rate limiting, and error handling for reliable search functionality."
                }
            ]
            
            # If you had an actual search API, you would process results here
            
            return jsonify({
                "status": "ok",
                "query": query,
                "results": search_results
            })
                
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
            
    logger.info("Multimedia API routes registered")


def create_uploads_dir():
    """Create the uploads directory if it doesn't exist."""
    uploads_dir = os.path.join('static', 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        logger.info(f"Created uploads directory: {uploads_dir}")
    else:
        logger.info(f"Uploads directory already exists at: {uploads_dir}")
    
    # Ensure the directory has proper permissions
    try:
        os.chmod(uploads_dir, 0o755)  # rwxr-xr-x
        logger.info("Set permissions on uploads directory")
    except Exception as e:
        logger.warning(f"Could not set permissions on uploads directory: {e}")
        
    # Log the details of the uploads directory
    logger.info(f"Uploads directory absolute path: {os.path.abspath(uploads_dir)}")
    logger.info(f"Uploads directory exists: {os.path.exists(uploads_dir)}")