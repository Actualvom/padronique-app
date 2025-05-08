/**
 * Camera Interface Module for Padronique AI Companion
 * Handles camera access, photo capture, and processing
 */

class CameraInterface {
    constructor() {
        // DOM Elements
        this.cameraBtn = document.getElementById('cameraBtn');
        this.closeCameraBtn = document.getElementById('closeCameraBtn');
        this.takePictureBtn = document.getElementById('takePictureBtn');
        this.switchCameraBtn = document.getElementById('switchCameraBtn');
        this.retakePictureBtn = document.getElementById('retakePictureBtn');
        this.usePictureBtn = document.getElementById('usePictureBtn');
        this.cameraContainer = document.getElementById('cameraContainer');
        this.cameraPreview = document.getElementById('cameraPreview');
        this.capturedImageContainer = document.getElementById('capturedImageContainer');
        this.capturedImage = document.getElementById('capturedImage');
        
        // State
        this.stream = null;
        this.facingMode = 'user'; // Front camera by default
        this.imageCapture = null;
        this.capturedImageBlob = null;
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize camera interface
     */
    init() {
        // Check if browser supports required APIs
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error('Camera access is not supported in this browser');
            this.cameraBtn.disabled = true;
            this.cameraBtn.title = 'Camera access not supported in your browser';
            return;
        }
        
        // Attach event listeners
        this.cameraBtn.addEventListener('click', () => this.showCamera());
        this.closeCameraBtn.addEventListener('click', () => this.hideCamera());
        this.takePictureBtn.addEventListener('click', () => this.takePicture());
        this.switchCameraBtn.addEventListener('click', () => this.switchCamera());
        this.retakePictureBtn.addEventListener('click', () => this.retakePicture());
        this.usePictureBtn.addEventListener('click', () => this.usePicture());
    }
    
    /**
     * Show camera interface and initialize camera
     */
    async showCamera() {
        this.cameraContainer.style.display = 'flex';
        this.capturedImageContainer.style.display = 'none';
        
        // Hide other containers
        document.querySelector('.voice-recording-container').style.display = 'none';
        document.getElementById('webSearchContainer').style.display = 'none';
        
        try {
            await this.startCamera();
        } catch (error) {
            console.error('Error starting camera:', error);
            alert('Could not access camera. Please check permissions and try again.');
            this.hideCamera();
        }
    }
    
    /**
     * Hide camera interface and stop camera
     */
    hideCamera() {
        this.stopCamera();
        this.cameraContainer.style.display = 'none';
    }
    
    /**
     * Start camera with current settings
     */
    async startCamera() {
        try {
            // Stop any existing stream
            this.stopCamera();
            
            // Get new stream
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: this.facingMode }
            });
            
            // Set video source
            this.cameraPreview.srcObject = this.stream;
            
            // Create ImageCapture object if supported
            if (window.ImageCapture) {
                const track = this.stream.getVideoTracks()[0];
                this.imageCapture = new ImageCapture(track);
            }
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            throw error;
        }
    }
    
    /**
     * Stop camera stream
     */
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.cameraPreview.srcObject = null;
        this.imageCapture = null;
    }
    
    /**
     * Switch between front and back camera
     */
    async switchCamera() {
        this.facingMode = this.facingMode === 'user' ? 'environment' : 'user';
        
        try {
            await this.startCamera();
        } catch (error) {
            console.error('Error switching camera:', error);
            // Revert back if failed
            this.facingMode = this.facingMode === 'user' ? 'environment' : 'user';
            alert('Could not switch camera. Your device might only have one camera.');
        }
    }
    
    /**
     * Take a picture
     */
    async takePicture() {
        try {
            let imageBlob;
            
            // Use ImageCapture API if available (higher quality)
            if (this.imageCapture) {
                const blob = await this.imageCapture.takePhoto();
                imageBlob = blob;
            } else {
                // Fallback to canvas method
                const canvas = document.createElement('canvas');
                canvas.width = this.cameraPreview.videoWidth;
                canvas.height = this.cameraPreview.videoHeight;
                
                const context = canvas.getContext('2d');
                context.drawImage(this.cameraPreview, 0, 0, canvas.width, canvas.height);
                
                // Convert to blob
                imageBlob = await new Promise(resolve => {
                    canvas.toBlob(blob => resolve(blob), 'image/jpeg', 0.95);
                });
            }
            
            // Show the captured image
            this.displayCapturedImage(imageBlob);
            this.capturedImageBlob = imageBlob;
            
        } catch (error) {
            console.error('Error taking picture:', error);
            alert('Failed to take picture. Please try again.');
        }
    }
    
    /**
     * Display captured image
     */
    displayCapturedImage(imageBlob) {
        const imageUrl = URL.createObjectURL(imageBlob);
        this.capturedImage.src = imageUrl;
        this.capturedImageContainer.style.display = 'block';
        this.cameraPreview.style.display = 'none';
        this.takePictureBtn.style.display = 'none';
        this.switchCameraBtn.style.display = 'none';
    }
    
    /**
     * Retake picture
     */
    retakePicture() {
        // Clear previous image
        if (this.capturedImage.src) {
            URL.revokeObjectURL(this.capturedImage.src);
        }
        
        // Reset UI
        this.capturedImageContainer.style.display = 'none';
        this.cameraPreview.style.display = 'block';
        this.takePictureBtn.style.display = 'inline-block';
        this.switchCameraBtn.style.display = 'inline-block';
        this.capturedImageBlob = null;
    }
    
    /**
     * Use captured picture in conversation
     */
    async usePicture() {
        if (!this.capturedImageBlob) {
            return;
        }
        
        try {
            // Create FormData for the API request
            const formData = new FormData();
            formData.append('image', this.capturedImageBlob, 'captured-image.jpg');
            
            // Send to API for processing
            const response = await fetch('/api/process-image', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'ok') {
                // Add image to chat
                this.addImageToChat(data.image_url, data.analysis);
                
                // Reset and hide camera UI
                this.hideCamera();
            } else {
                throw new Error('Image processing failed');
            }
        } catch (error) {
            console.error('Error processing image:', error);
            alert('Failed to process image. Please try again.');
        }
    }
    
    /**
     * Add image to chat
     */
    addImageToChat(imageUrl, analysis) {
        // Check if we have a global function for adding messages
        if (window.addMessageToChat) {
            window.addMessageToChat('user', null, imageUrl);
            
            // Let the AI process the image
            window.sendMessage(`[Image uploaded. Please analyze it.]`);
        } else {
            // Fallback if addMessageToChat is not globally available
            const chatMessages = document.getElementById('chat-messages');
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            
            // Create user message with image
            const messageElement = document.createElement('div');
            messageElement.className = 'message user';
            
            const contentElement = document.createElement('div');
            contentElement.className = 'message-content';
            
            const imageElement = document.createElement('img');
            imageElement.src = imageUrl;
            imageElement.className = 'message-image';
            imageElement.alt = 'Uploaded image';
            
            contentElement.appendChild(imageElement);
            messageElement.appendChild(contentElement);
            
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Send message about the image
            messageInput.value = `[Image uploaded. Please analyze it.]`;
            sendBtn.click();
        }
    }
}

// Export for use in other modules
window.CameraInterface = CameraInterface;