/**
 * Voice Interface Module for Padronique AI Companion
 * Handles voice recording, transcription, and interaction
 */

class VoiceInterface {
    constructor() {
        // DOM Elements
        this.voiceBtn = document.getElementById('voiceBtn');
        this.stopRecordingBtn = document.getElementById('stopRecordingBtn');
        this.cancelRecordingBtn = document.getElementById('cancelRecordingBtn');
        this.sendVoiceBtn = document.getElementById('sendVoiceBtn');
        this.editVoiceBtn = document.getElementById('editVoiceBtn');
        this.voiceRecordingContainer = document.querySelector('.voice-recording-container');
        this.voicePreview = document.getElementById('voicePreview');
        this.previewText = document.querySelector('.preview-text');
        this.messageInput = document.getElementById('messageInput');
        
        // State
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize voice interface
     */
    init() {
        // Check if browser supports required APIs
        if (!navigator.mediaDevices || !window.MediaRecorder) {
            console.error('Voice recording is not supported in this browser');
            this.voiceBtn.disabled = true;
            this.voiceBtn.title = 'Voice recording not supported in your browser';
            return;
        }
        
        // Attach event listeners
        this.voiceBtn.addEventListener('click', () => this.startRecording());
        this.stopRecordingBtn.addEventListener('click', () => this.stopRecording());
        this.cancelRecordingBtn.addEventListener('click', () => this.cancelRecording());
        this.sendVoiceBtn.addEventListener('click', () => this.sendVoiceMessage());
        this.editVoiceBtn.addEventListener('click', () => this.editVoiceMessage());
    }
    
    /**
     * Start voice recording
     */
    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.audioChunks = [];
            
            this.mediaRecorder.addEventListener('dataavailable', event => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            });
            
            this.mediaRecorder.addEventListener('stop', () => {
                if (this.isRecording) {
                    this.processAudio();
                }
            });
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Show recording UI
            this.voiceRecordingContainer.style.display = 'flex';
            this.voicePreview.style.display = 'none';
            
            console.log('Voice recording started');
        } catch (error) {
            console.error('Error starting voice recording:', error);
            alert('Could not access microphone. Please check permissions and try again.');
        }
    }
    
    /**
     * Stop voice recording
     */
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Update UI
            document.querySelector('.voice-status').textContent = 'Processing...';
            
            // Stop all tracks on the stream
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
                this.stream = null;
            }
            
            console.log('Voice recording stopped');
        }
    }
    
    /**
     * Cancel voice recording
     */
    cancelRecording() {
        if (this.mediaRecorder) {
            if (this.isRecording) {
                this.mediaRecorder.stop();
                this.isRecording = false;
            }
            
            // Stop all tracks on the stream
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
                this.stream = null;
            }
        }
        
        // Reset and hide UI
        this.voiceRecordingContainer.style.display = 'none';
        this.audioChunks = [];
        
        console.log('Voice recording cancelled');
    }
    
    /**
     * Process recorded audio
     */
    async processAudio() {
        if (this.audioChunks.length === 0) {
            this.cancelRecording();
            return;
        }
        
        try {
            // Create audio blob and file
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            const audioFile = new File([audioBlob], 'voice-message.webm', { type: 'audio/webm' });
            
            // Create FormData for the API request
            const formData = new FormData();
            formData.append('audio', audioFile);
            
            // Update UI
            document.querySelector('.voice-status').textContent = 'Transcribing...';
            
            // Send to API for transcription
            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'ok' && data.text) {
                // Show preview with transcribed text
                this.previewText.textContent = data.text;
                this.voicePreview.style.display = 'block';
                document.querySelector('.voice-status').textContent = 'Voice message ready';
            } else {
                throw new Error('Transcription failed or returned empty text');
            }
        } catch (error) {
            console.error('Error processing audio:', error);
            document.querySelector('.voice-status').textContent = 'Error processing audio';
            
            // Show retry button
            this.voicePreview.style.display = 'block';
            this.previewText.textContent = 'Sorry, there was an error transcribing your voice message. Please try again.';
        }
    }
    
    /**
     * Send voice message after transcription
     */
    sendVoiceMessage() {
        const transcribedText = this.previewText.textContent;
        
        if (transcribedText && transcribedText !== 'Sorry, there was an error transcribing your voice message. Please try again.') {
            // Reset and hide voice UI
            this.voiceRecordingContainer.style.display = 'none';
            
            // Trigger message send with transcribed text
            if (window.sendMessage) {
                window.sendMessage(transcribedText);
            } else {
                // Fallback if sendMessage is not globally available
                // Get reference to chat functionality
                const messageInput = document.getElementById('messageInput');
                const sendBtn = document.getElementById('sendBtn');
                
                // Set input value and trigger send button
                messageInput.value = transcribedText;
                sendBtn.click();
            }
        }
    }
    
    /**
     * Edit transcribed voice message
     */
    editVoiceMessage() {
        const transcribedText = this.previewText.textContent;
        
        if (transcribedText && transcribedText !== 'Sorry, there was an error transcribing your voice message. Please try again.') {
            // Set transcribed text to message input
            this.messageInput.value = transcribedText;
            
            // Reset and hide voice UI
            this.voiceRecordingContainer.style.display = 'none';
            
            // Focus on the input for editing
            this.messageInput.focus();
        }
    }
}

// Export for use in other modules
window.VoiceInterface = VoiceInterface;