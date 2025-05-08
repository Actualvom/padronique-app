/**
 * Confirmation Dialog System for Padronique
 * 
 * Provides multi-step confirmation for destructive actions
 * to prevent accidental data loss.
 */

class ConfirmationDialog {
    constructor() {
        this.dialogElement = null;
        this.overlayElement = null;
        this.confirmCallback = null;
        this.cancelCallback = null;
        this.currentStep = 0;
        this.maxSteps = 0;
        this.actionType = '';
        
        this.init();
    }
    
    init() {
        // Create dialog elements if they don't exist
        if (!document.getElementById('confirmation-dialog')) {
            this.createDialogElements();
        } else {
            this.dialogElement = document.getElementById('confirmation-dialog');
            this.overlayElement = document.getElementById('dialog-overlay');
        }
        
        // Add event listeners
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isVisible()) {
                this.hide();
            }
        });
    }
    
    createDialogElements() {
        // Create overlay
        this.overlayElement = document.createElement('div');
        this.overlayElement.id = 'dialog-overlay';
        this.overlayElement.className = 'dialog-overlay';
        this.overlayElement.style.display = 'none';
        
        // Create dialog
        this.dialogElement = document.createElement('div');
        this.dialogElement.id = 'confirmation-dialog';
        this.dialogElement.className = 'confirmation-dialog';
        this.dialogElement.style.display = 'none';
        
        // Add inner structure
        this.dialogElement.innerHTML = `
            <div class="dialog-header">
                <h3 id="dialog-title">Confirmation Required</h3>
                <button class="close-button" id="dialog-close">×</button>
            </div>
            <div class="dialog-content">
                <p id="dialog-message">Are you sure you want to proceed with this action?</p>
                <div id="dialog-warning-icon" class="warning-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="64" height="64">
                        <path fill="none" stroke="#ff3b30" stroke-width="2" d="M12 1L1 21h22L12 1z" />
                        <path fill="#ff3b30" d="M12 16a1 1 0 100 2 1 1 0 000-2z" />
                        <path fill="none" stroke="#ff3b30" stroke-width="2" d="M12 7v6" />
                    </svg>
                </div>
                <div id="dialog-step-indicator" class="step-indicator">
                    <span class="current-step">1</span>/<span class="total-steps">3</span>
                </div>
                <div id="dialog-checkbox-container" class="checkbox-container">
                    <input type="checkbox" id="confirm-checkbox">
                    <label for="confirm-checkbox" id="checkbox-label">I understand this action cannot be undone</label>
                </div>
                <div id="dialog-input-container" class="input-container">
                    <label for="confirm-input" id="input-label">Type "DELETE" to confirm:</label>
                    <input type="text" id="confirm-input" autocomplete="off">
                </div>
            </div>
            <div class="dialog-footer">
                <button id="dialog-cancel" class="btn btn-secondary">Cancel</button>
                <button id="dialog-confirm" class="btn btn-danger" disabled>Confirm</button>
            </div>
        `;
        
        // Add to DOM
        document.body.appendChild(this.overlayElement);
        document.body.appendChild(this.dialogElement);
        
        // Setup event listeners
        document.getElementById('dialog-close').addEventListener('click', () => this.hide());
        document.getElementById('dialog-cancel').addEventListener('click', () => this.hide());
        document.getElementById('dialog-confirm').addEventListener('click', () => this.nextStep());
        
        // Checkbox event listener
        document.getElementById('confirm-checkbox').addEventListener('change', (e) => {
            if (this.currentStep === 1) {
                document.getElementById('dialog-confirm').disabled = !e.target.checked;
            }
        });
        
        // Text input event listener
        document.getElementById('confirm-input').addEventListener('input', (e) => {
            if (this.currentStep === 2) {
                const confirmBtn = document.getElementById('dialog-confirm');
                if (this.actionType === 'reset') {
                    confirmBtn.disabled = e.target.value !== 'RESET';
                } else {
                    confirmBtn.disabled = e.target.value !== 'DELETE';
                }
            }
        });
        
        // Clicking overlay closes dialog
        this.overlayElement.addEventListener('click', (e) => {
            if (e.target === this.overlayElement) {
                this.hide();
            }
        });
    }
    
    showForAction(actionType, confirmCallback, cancelCallback = null) {
        this.actionType = actionType;
        this.confirmCallback = confirmCallback;
        this.cancelCallback = cancelCallback;
        this.currentStep = 1;
        
        // Configure based on action type
        let title, message, maxSteps;
        
        switch (actionType) {
            case 'clear-chat':
                title = 'Clear Chat History';
                message = 'This will permanently delete all chat messages. This action cannot be undone.';
                maxSteps = 3;
                break;
            case 'reset':
                title = 'Reset System';
                message = 'This will reset Padronique to its default state, deleting all memories, preferences, and history. This action cannot be undone.';
                maxSteps = 3;
                break;
            case 'export':
                title = 'Export Memory Archive';
                message = 'This will download an archive of all memories and interactions. Your data will remain intact in the system.';
                maxSteps = 1;
                break;
            default:
                title = 'Confirmation Required';
                message = 'Are you sure you want to proceed with this action?';
                maxSteps = 2;
        }
        
        this.maxSteps = maxSteps;
        
        // Update dialog content
        document.getElementById('dialog-title').textContent = title;
        document.getElementById('dialog-message').textContent = message;
        
        // Update step indicator
        document.querySelector('.current-step').textContent = this.currentStep;
        document.querySelector('.total-steps').textContent = this.maxSteps;
        
        // Configure step-specific elements
        this.configureStepElements();
        
        // Show dialog
        this.overlayElement.style.display = 'block';
        this.dialogElement.style.display = 'block';
    }
    
    configureStepElements() {
        const checkboxContainer = document.getElementById('dialog-checkbox-container');
        const inputContainer = document.getElementById('dialog-input-container');
        const confirmBtn = document.getElementById('dialog-confirm');
        const checkbox = document.getElementById('confirm-checkbox');
        const input = document.getElementById('confirm-input');
        const stepIndicator = document.getElementById('dialog-step-indicator');
        
        // Reset state
        checkbox.checked = false;
        input.value = '';
        confirmBtn.disabled = true;
        
        // Show/hide elements based on current step
        if (this.maxSteps === 1) {
            // For non-destructive actions like export
            checkboxContainer.style.display = 'none';
            inputContainer.style.display = 'none';
            stepIndicator.style.display = 'none';
            confirmBtn.disabled = false;
        } else {
            stepIndicator.style.display = 'block';
            
            if (this.currentStep === 1) {
                checkboxContainer.style.display = 'block';
                inputContainer.style.display = 'none';
                document.getElementById('checkbox-label').textContent = 
                    this.actionType === 'reset' 
                        ? 'I understand this will delete all system data and cannot be undone' 
                        : 'I understand this will delete my chat history and cannot be undone';
            } else if (this.currentStep === 2) {
                checkboxContainer.style.display = 'none';
                inputContainer.style.display = 'block';
                
                if (this.actionType === 'reset') {
                    document.getElementById('input-label').textContent = 'Type "RESET" to confirm:';
                } else {
                    document.getElementById('input-label').textContent = 'Type "DELETE" to confirm:';
                }
            } else if (this.currentStep === 3 && this.maxSteps === 3) {
                // Final verification for 3-step processes
                checkboxContainer.style.display = 'none';
                inputContainer.style.display = 'none';
                document.getElementById('dialog-message').textContent = 
                    this.actionType === 'reset' 
                        ? 'Are you absolutely sure you want to reset the entire system? This is your last chance to cancel.'
                        : 'Are you absolutely sure you want to delete all chat history? This is your last chance to cancel.';
                confirmBtn.disabled = false;
            }
        }
    }
    
    nextStep() {
        if (this.currentStep < this.maxSteps) {
            this.currentStep++;
            document.querySelector('.current-step').textContent = this.currentStep;
            this.configureStepElements();
        } else {
            // Final confirmation
            this.hide();
            if (typeof this.confirmCallback === 'function') {
                this.confirmCallback();
            }
        }
    }
    
    hide() {
        this.overlayElement.style.display = 'none';
        this.dialogElement.style.display = 'none';
        
        if (this.currentStep < this.maxSteps && typeof this.cancelCallback === 'function') {
            this.cancelCallback();
        }
    }
    
    isVisible() {
        return this.dialogElement.style.display === 'block';
    }
}

// Global instance
const confirmationDialog = new ConfirmationDialog();

// Export functions for use in main app
function showClearChatConfirmation(confirmCallback) {
    confirmationDialog.showForAction('clear-chat', confirmCallback);
}

function showResetSystemConfirmation(confirmCallback) {
    confirmationDialog.showForAction('reset', confirmCallback);
}

function showExportConfirmation(confirmCallback) {
    confirmationDialog.showForAction('export', confirmCallback);
}