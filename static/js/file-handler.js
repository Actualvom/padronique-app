/**
 * File Handler Module for Padronique AI Companion
 * Handles file uploads and processing
 */

class FileHandler {
    constructor() {
        // DOM Elements
        this.fileUploadBtn = document.getElementById('fileUploadBtn');
        this.fileInput = document.getElementById('fileInput');
        
        // State
        this.maxFileSizeMB = 10; // Maximum file size in MB
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize file handler
     */
    init() {
        // Attach event listeners
        this.fileUploadBtn.addEventListener('click', () => this.triggerFileInput());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelection(e));
    }
    
    /**
     * Trigger file input dialog
     */
    triggerFileInput() {
        this.fileInput.click();
    }
    
    /**
     * Handle file selection
     */
    async handleFileSelection(event) {
        const file = event.target.files[0];
        
        if (!file) {
            return;
        }
        
        // Check file size
        if (file.size > this.maxFileSizeMB * 1024 * 1024) {
            alert(`File size exceeds the maximum limit of ${this.maxFileSizeMB}MB`);
            this.fileInput.value = '';
            return;
        }
        
        try {
            await this.processFile(file);
        } catch (error) {
            console.error('Error processing file:', error);
            alert('Failed to process file. Please try again with a different file.');
        }
        
        // Reset file input
        this.fileInput.value = '';
    }
    
    /**
     * Process the selected file
     */
    async processFile(file) {
        // Create FormData for the API request
        const formData = new FormData();
        formData.append('file', file);
        
        // Add a loading message to chat
        this.addLoadingMessage(`Uploading and processing ${file.name}...`);
        
        try {
            // Send to API for processing
            const response = await fetch('/api/process-file', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove loading message
            this.removeLoadingMessage();
            
            if (data.status === 'ok') {
                // Add file to chat
                this.addFileToChat(file.name, file.type, data.content || data.url);
                
                // Send message to process the file
                this.sendFileAnalysisRequest(file.name, file.type);
            } else {
                throw new Error('File processing failed');
            }
        } catch (error) {
            console.error('Error processing file:', error);
            
            // Remove loading message
            this.removeLoadingMessage();
            
            // Add error message
            this.addErrorMessage(`Failed to process ${file.name}`);
        }
    }
    
    /**
     * Add loading message to chat
     */
    addLoadingMessage(text) {
        if (window.addMessageToChat) {
            window.loadingMessageId = Date.now().toString();
            window.addMessageToChat('system', text, null, window.loadingMessageId);
        } else {
            // Fallback
            const chatMessages = document.getElementById('chat-messages');
            
            const messageElement = document.createElement('div');
            messageElement.className = 'message system loading-message';
            messageElement.id = 'loading-message';
            
            const contentElement = document.createElement('div');
            contentElement.className = 'message-content';
            
            const textElement = document.createElement('p');
            textElement.textContent = text;
            
            contentElement.appendChild(textElement);
            messageElement.appendChild(contentElement);
            
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    /**
     * Remove loading message from chat
     */
    removeLoadingMessage() {
        if (window.loadingMessageId) {
            const loadingMessage = document.querySelector(`[data-message-id="${window.loadingMessageId}"]`);
            if (loadingMessage) {
                loadingMessage.remove();
            }
            window.loadingMessageId = null;
        } else {
            // Fallback
            const loadingMessage = document.getElementById('loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        }
    }
    
    /**
     * Add error message to chat
     */
    addErrorMessage(text) {
        if (window.addMessageToChat) {
            window.addMessageToChat('system', text);
        } else {
            // Fallback
            const chatMessages = document.getElementById('chat-messages');
            
            const messageElement = document.createElement('div');
            messageElement.className = 'message system';
            
            const contentElement = document.createElement('div');
            contentElement.className = 'message-content';
            
            const textElement = document.createElement('p');
            textElement.textContent = text;
            textElement.className = 'text-danger';
            
            contentElement.appendChild(textElement);
            messageElement.appendChild(contentElement);
            
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    /**
     * Add file to chat
     */
    addFileToChat(fileName, fileType, content) {
        if (window.addMessageToChat) {
            // Check if it's an image
            const isImage = fileType.startsWith('image/');
            
            if (isImage && content.startsWith('data:')) {
                // It's an image with data URL
                window.addMessageToChat('user', null, content);
            } else {
                // Text or other type of file
                const fileIcon = this.getFileIcon(fileType);
                const fileDisplay = `<div class="file-attachment">
                    <div class="file-icon"><i class="${fileIcon}"></i></div>
                    <div class="file-details">
                        <div class="file-name">${this.escapeHtml(fileName)}</div>
                        <div class="file-type">${this.formatFileType(fileType)}</div>
                    </div>
                </div>`;
                
                window.addMessageToChat('user', fileDisplay);
            }
        } else {
            // Fallback
            const chatMessages = document.getElementById('chat-messages');
            
            const messageElement = document.createElement('div');
            messageElement.className = 'message user';
            
            const contentElement = document.createElement('div');
            contentElement.className = 'message-content';
            
            // Check if it's an image
            const isImage = fileType.startsWith('image/');
            
            if (isImage && content.startsWith('data:')) {
                // Display image
                const imageElement = document.createElement('img');
                imageElement.src = content;
                imageElement.className = 'message-image';
                imageElement.alt = fileName;
                
                contentElement.appendChild(imageElement);
            } else {
                // Display file attachment
                const fileAttachment = document.createElement('div');
                fileAttachment.className = 'file-attachment';
                
                const fileIcon = this.getFileIcon(fileType);
                fileAttachment.innerHTML = `
                    <div class="file-icon"><i class="${fileIcon}"></i></div>
                    <div class="file-details">
                        <div class="file-name">${this.escapeHtml(fileName)}</div>
                        <div class="file-type">${this.formatFileType(fileType)}</div>
                    </div>
                `;
                
                contentElement.appendChild(fileAttachment);
            }
            
            messageElement.appendChild(contentElement);
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    /**
     * Send a request for the AI to analyze the uploaded file
     */
    sendFileAnalysisRequest(fileName, fileType) {
        const messageText = this.generateFileAnalysisPrompt(fileName, fileType);
        
        if (window.sendMessage) {
            window.sendMessage(messageText);
        } else {
            // Fallback
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            
            messageInput.value = messageText;
            sendBtn.click();
        }
    }
    
    /**
     * Generate appropriate prompt for file analysis
     */
    generateFileAnalysisPrompt(fileName, fileType) {
        if (fileType.startsWith('image/')) {
            return `I've uploaded an image file "${fileName}". Please analyze it.`;
        } else if (fileType === 'application/pdf') {
            return `I've uploaded a PDF file "${fileName}". Please analyze its content.`;
        } else if (fileType === 'text/plain') {
            return `I've uploaded a text file "${fileName}". Please analyze its content.`;
        } else if (fileType.includes('document') || fileType.includes('msword') || fileType.includes('officedocument')) {
            return `I've uploaded a document "${fileName}". Please analyze its content.`;
        } else {
            return `I've uploaded a file "${fileName}" (${fileType}). Please analyze it if possible.`;
        }
    }
    
    /**
     * Get appropriate icon for file type
     */
    getFileIcon(fileType) {
        if (fileType.startsWith('image/')) {
            return 'fas fa-file-image';
        } else if (fileType === 'application/pdf') {
            return 'fas fa-file-pdf';
        } else if (fileType === 'text/plain') {
            return 'fas fa-file-alt';
        } else if (fileType.includes('document') || fileType.includes('msword') || fileType.includes('officedocument')) {
            return 'fas fa-file-word';
        } else {
            return 'fas fa-file';
        }
    }
    
    /**
     * Format file type for display
     */
    formatFileType(fileType) {
        const types = {
            'image/jpeg': 'JPEG Image',
            'image/png': 'PNG Image',
            'image/gif': 'GIF Image',
            'image/svg+xml': 'SVG Image',
            'application/pdf': 'PDF Document',
            'text/plain': 'Text File',
            'application/msword': 'Word Document',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Document',
            'application/vnd.ms-excel': 'Excel Spreadsheet',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel Spreadsheet'
        };
        
        return types[fileType] || fileType;
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export for use in other modules
window.FileHandler = FileHandler;