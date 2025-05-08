/**
 * Padronique AI Companion - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation
    initNavigation();
    
    // Initialize chat functionality
    initChat();
    
    // Initialize memory page
    initMemory();
    
    // Initialize dashboard
    initDashboard();
    
    // Initialize settings
    initSettings();
    
    // Initialize confirmation dialogs for destructive actions
    initConfirmationDialogs();
    
    // Initialize specialized modules
    initModules();
    
    // Fetch initial system status
    fetchSystemStatus();
    
    console.log('Padronique AI Companion initialized');
});

/**
 * Initialize specialized functional modules
 */
function initModules() {
    // Voice Interface
    if (window.VoiceInterface && document.getElementById('voiceBtn')) {
        window.voiceInterface = new VoiceInterface();
        console.log('Voice Interface initialized');
    } else {
        console.warn('Voice Interface not available or voiceBtn not found');
    }
    
    // File Handler
    if (window.FileHandler && document.getElementById('fileUploadBtn')) {
        window.fileHandler = new FileHandler();
        console.log('File Handler initialized');
    } else {
        console.warn('File Handler not available or fileUploadBtn not found');
    }
    
    // Camera Interface
    if (window.CameraInterface && document.getElementById('cameraBtn')) {
        window.cameraInterface = new CameraInterface();
        console.log('Camera Interface initialized');
    } else {
        console.warn('Camera Interface not available or cameraBtn not found');
    }
    
    // Web Search
    if (window.WebSearch && document.getElementById('webSearchBtn')) {
        window.webSearch = new WebSearch();
        console.log('Web Search initialized');
    } else {
        console.warn('Web Search not available or webSearchBtn not found');
    }
    
    // Make sendMessage global for module use
    if (typeof sendMessage === 'function') {
        window.sendMessage = sendMessage;
    } else {
        console.warn('sendMessage function not available for module integration');
    }
}

/**
 * Initialize navigation between pages
 */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const pageName = this.getAttribute('data-page');
            
            // Remove active class from all nav items and pages
            document.querySelectorAll('.nav-item').forEach(navItem => {
                navItem.classList.remove('active');
            });
            
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // Add active class to clicked nav item and corresponding page
            this.classList.add('active');
            document.getElementById(`${pageName}-page`).classList.add('active');
        });
    });
}

/**
 * Initialize chat functionality
 */
function initChat() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chat-messages');
    
    // Send message on button click
    sendBtn.addEventListener('click', function() {
        sendMessage();
    });
    
    // Send message on Enter key
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Function to send message
    function sendMessage() {
        const message = messageInput.value.trim();
        
        if (message) {
            // Add user message to chat
            addMessageToChat('user', message);
            
            // Clear input
            messageInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send to API
            fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: message,
                    type: 'text'
                })
            })
            .then(response => response.json())
            .then(data => {
                // Hide typing indicator
                hideTypingIndicator();
                
                // Add AI response to chat
                if (data.status === 'ok') {
                    // Check if response is an object with content property
                    if (data.response && typeof data.response === 'object' && data.response.content) {
                        addMessageToChat('ai', data.response.content);
                    } else {
                        addMessageToChat('ai', data.response);
                    }
                } else {
                    addMessageToChat('system', 'Sorry, I encountered an error processing your message.');
                }
            })
            .catch(error => {
                console.error('Error sending message:', error);
                hideTypingIndicator();
                addMessageToChat('system', 'Sorry, there was a network error. Please try again.');
            });
        }
    }
    
    // Add message to chat
    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        
        const textElement = document.createElement('p');
        textElement.style.whiteSpace = 'normal'; // Force normal text wrapping
        textElement.style.wordBreak = 'break-word'; // Allow word breaking if needed
        
        // Handle different types of messages
        if (message === null || message === undefined) {
            textElement.textContent = "No response received.";
        } else if (typeof message === 'object') {
            // If message is an object, stringify it properly
            try {
                textElement.textContent = JSON.stringify(message, null, 2);
            } catch (e) {
                textElement.textContent = "Received an object that couldn't be displayed properly.";
            }
        } else {
            textElement.textContent = message;
        }
        
        contentElement.appendChild(textElement);
        messageElement.appendChild(contentElement);
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        if (!document.querySelector('.typing-indicator')) {
            const indicatorElement = document.createElement('div');
            indicatorElement.className = 'message ai typing-indicator';
            
            const contentElement = document.createElement('div');
            contentElement.className = 'message-content';
            
            const dotsElement = document.createElement('div');
            dotsElement.className = 'typing-dots';
            
            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('span');
                dot.className = 'dot';
                dotsElement.appendChild(dot);
            }
            
            contentElement.appendChild(dotsElement);
            indicatorElement.appendChild(contentElement);
            
            chatMessages.appendChild(indicatorElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
}

/**
 * Initialize memory page
 */
function initMemory() {
    const refreshMemoryBtn = document.getElementById('refreshMemoryBtn');
    const memorySearchBtn = document.getElementById('memorySearchBtn');
    const memorySearchInput = document.getElementById('memorySearchInput');
    
    // Refresh memory list
    refreshMemoryBtn.addEventListener('click', function() {
        fetchMemories();
    });
    
    // Search memories
    memorySearchBtn.addEventListener('click', function() {
        const query = memorySearchInput.value.trim();
        fetchMemories(query);
    });
    
    // Search on Enter key
    memorySearchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.trim();
            fetchMemories(query);
        }
    });
    
    // Filter by memory type
    document.querySelectorAll('[data-filter]').forEach(filterBtn => {
        filterBtn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            fetchMemories('', filter);
        });
    });
    
    // Function to fetch memories
    function fetchMemories(query = '', filter = 'all') {
        const memoryGrid = document.getElementById('memory-grid');
        
        // Show loading state
        memoryGrid.innerHTML = '<div class="memory-loading"><i class="fas fa-spinner fa-spin"></i><p>Loading memories...</p></div>';
        
        let url = '/api/memory';
        const params = new URLSearchParams();
        
        if (query) {
            params.append('query', query);
        }
        
        if (filter !== 'all') {
            params.append('tags', filter);
        }
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok' && data.memories && data.memories.length > 0) {
                    // Display memories
                    displayMemories(data.memories);
                } else {
                    // No memories found
                    memoryGrid.innerHTML = '<div class="memory-placeholder"><i class="fas fa-brain"></i><p>No memories found</p></div>';
                }
            })
            .catch(error => {
                console.error('Error fetching memories:', error);
                memoryGrid.innerHTML = '<div class="memory-placeholder"><i class="fas fa-exclamation-triangle"></i><p>Error loading memories</p></div>';
            });
    }
    
    // Function to display memories
    function displayMemories(memories) {
        const memoryGrid = document.getElementById('memory-grid');
        memoryGrid.innerHTML = '';
        
        memories.forEach(memory => {
            const memoryElement = document.createElement('div');
            memoryElement.className = 'memory-item';
            memoryElement.setAttribute('data-id', memory.id);
            
            const memoryHeader = document.createElement('div');
            memoryHeader.className = 'memory-header';
            
            const memoryType = document.createElement('div');
            memoryType.className = 'memory-type';
            memoryType.textContent = memory.memory_type;
            
            const memoryImportance = document.createElement('div');
            memoryImportance.className = 'memory-importance';
            
            // Create stars based on importance
            const stars = Math.round(memory.importance * 5);
            for (let i = 0; i < 5; i++) {
                const star = document.createElement('i');
                star.className = i < stars ? 'fas fa-star' : 'far fa-star';
                memoryImportance.appendChild(star);
            }
            
            memoryHeader.appendChild(memoryType);
            memoryHeader.appendChild(memoryImportance);
            
            const memoryContent = document.createElement('div');
            memoryContent.className = 'memory-content';
            memoryContent.textContent = memory.content;
            
            const memoryFooter = document.createElement('div');
            memoryFooter.className = 'memory-footer';
            
            const memoryDate = document.createElement('div');
            memoryDate.className = 'memory-date';
            
            // Format date
            const date = new Date(memory.created_at);
            memoryDate.textContent = date.toLocaleDateString();
            
            const memoryActions = document.createElement('div');
            memoryActions.className = 'memory-actions';
            
            const expandBtn = document.createElement('button');
            expandBtn.className = 'memory-action-btn';
            expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
            expandBtn.addEventListener('click', function() {
                // View memory details
                viewMemoryDetails(memory.id);
            });
            
            memoryActions.appendChild(expandBtn);
            memoryFooter.appendChild(memoryDate);
            memoryFooter.appendChild(memoryActions);
            
            memoryElement.appendChild(memoryHeader);
            memoryElement.appendChild(memoryContent);
            memoryElement.appendChild(memoryFooter);
            
            memoryGrid.appendChild(memoryElement);
        });
    }
    
    // Function to view memory details
    function viewMemoryDetails(memoryId) {
        // Functionality to be implemented
        console.log('View memory details:', memoryId);
    }
}

/**
 * Initialize dashboard functionality
 */
function initDashboard() {
    const refreshDashboardBtn = document.getElementById('refreshDashboardBtn');
    
    // Refresh dashboard
    refreshDashboardBtn.addEventListener('click', function() {
        fetchSystemStatus();
    });
}

/**
 * Initialize settings functionality
 */
function initSettings() {
    // User name input
    const userNameInput = document.getElementById('userNameInput');
    userNameInput.addEventListener('change', function() {
        // Save user name
        saveSettings('username', this.value);
    });
    
    // Theme selection
    const themeSelect = document.getElementById('themeSelect');
    themeSelect.addEventListener('change', function() {
        // Apply theme
        applyTheme(this.value);
        // Save theme preference
        saveSettings('theme', this.value);
    });
    
    // Data collection toggle
    const dataCollectionToggle = document.getElementById('dataCollectionToggle');
    dataCollectionToggle.addEventListener('change', function() {
        // Save data collection preference
        saveSettings('data_collection', this.checked);
    });
    
    // External connections toggle
    const externalConnectionsToggle = document.getElementById('externalConnectionsToggle');
    externalConnectionsToggle.addEventListener('change', function() {
        // Save external connections preference
        saveSettings('external_connections', this.checked);
    });
    
    // Debug mode toggle
    const debugModeToggle = document.getElementById('debugModeToggle');
    debugModeToggle.addEventListener('change', function() {
        // Save debug mode preference
        saveSettings('debug_mode', this.checked);
    });
    
    // Function to apply theme
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
    }
    
    // Function to save settings
    function saveSettings(key, value) {
        // Store in local storage for now
        localStorage.setItem(`padronique_${key}`, JSON.stringify(value));
        
        // In a full implementation, this would be sent to the API
        console.log(`Setting saved: ${key} = ${value}`);
    }
    
    // Load saved settings
    function loadSettings() {
        // User name
        const savedUsername = localStorage.getItem('padronique_username');
        if (savedUsername) {
            userNameInput.value = JSON.parse(savedUsername);
        }
        
        // Theme
        const savedTheme = localStorage.getItem('padronique_theme');
        if (savedTheme) {
            const theme = JSON.parse(savedTheme);
            themeSelect.value = theme;
            applyTheme(theme);
        }
        
        // Data collection
        const savedDataCollection = localStorage.getItem('padronique_data_collection');
        if (savedDataCollection !== null) {
            dataCollectionToggle.checked = JSON.parse(savedDataCollection);
        }
        
        // External connections
        const savedExternalConnections = localStorage.getItem('padronique_external_connections');
        if (savedExternalConnections !== null) {
            externalConnectionsToggle.checked = JSON.parse(savedExternalConnections);
        }
        
        // Debug mode
        const savedDebugMode = localStorage.getItem('padronique_debug_mode');
        if (savedDebugMode !== null) {
            debugModeToggle.checked = JSON.parse(savedDebugMode);
        }
    }
    
    // Initialize settings
    loadSettings();
}

/**
 * Initialize confirmation dialogs for destructive actions
 */
function initConfirmationDialogs() {
    // Get all buttons that need confirmation
    const clearChatBtn = document.getElementById('clearChatBtn');
    const resetSystemBtn = document.getElementById('resetSystemBtn');
    const exportMemoryBtn = document.getElementById('exportMemoryBtn');
    
    // Settings page buttons
    const clearChatSettingsBtn = document.getElementById('clearChatSettingsBtn');
    const resetSystemSettingsBtn = document.getElementById('resetSystemSettingsBtn');
    const exportMemorySettingsBtn = document.getElementById('exportMemorySettingsBtn');
    
    // Clear chat history confirmation
    [clearChatBtn, clearChatSettingsBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                showClearChatConfirmation(function() {
                    // This function is called when the user confirms
                    clearChatHistory();
                });
            });
        }
    });
    
    // Reset system confirmation
    [resetSystemBtn, resetSystemSettingsBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                showResetSystemConfirmation(function() {
                    // This function is called when the user confirms
                    resetSystem();
                });
            });
        }
    });
    
    // Export memory confirmation (less strict, only 1 step)
    [exportMemoryBtn, exportMemorySettingsBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                showExportConfirmation(function() {
                    // This function is called when the user confirms
                    exportMemoryArchive();
                });
            });
        }
    });
}

/**
 * Clear chat history
 */
function clearChatHistory() {
    const chatMessages = document.getElementById('chat-messages');
    
    // Keep only the welcome message
    const welcomeMessage = chatMessages.querySelector('.message.system');
    chatMessages.innerHTML = '';
    
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage);
    } else {
        // If welcome message was removed, create a new one
        const newWelcomeMessage = document.createElement('div');
        newWelcomeMessage.className = 'message system';
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        
        const textElement = document.createElement('p');
        textElement.textContent = 'Chat history has been cleared. How can I assist you today?';
        
        contentElement.appendChild(textElement);
        newWelcomeMessage.appendChild(contentElement);
        
        chatMessages.appendChild(newWelcomeMessage);
    }
    
    // Send clear chat request to API
    fetch('/api/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: 'chat_history'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Chat history cleared:', data);
    })
    .catch(error => {
        console.error('Error clearing chat history:', error);
    });
}

/**
 * Reset the system
 */
function resetSystem() {
    // Send reset request to API
    fetch('/api/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: 'full_system'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('System reset:', data);
        
        // Show reset confirmation message
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = '';
        
        const resetMessage = document.createElement('div');
        resetMessage.className = 'message system';
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        
        const textElement = document.createElement('p');
        textElement.textContent = 'System has been reset. Welcome to Padronique AI Companion.';
        
        contentElement.appendChild(textElement);
        resetMessage.appendChild(contentElement);
        
        chatMessages.appendChild(resetMessage);
        
        // Refresh the dashboard
        fetchSystemStatus();
    })
    .catch(error => {
        console.error('Error resetting system:', error);
    });
}

/**
 * Export memory archive
 */
function exportMemoryArchive() {
    // In a real implementation, this would download an actual file
    // For this demo, we'll just show a message
    
    const chatMessages = document.getElementById('chat-messages');
    
    // Add a message to the chat
    const messageElement = document.createElement('div');
    messageElement.className = 'message system';
    
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    
    const textElement = document.createElement('p');
    textElement.textContent = 'Memory archive export initiated. Your file will be ready for download shortly.';
    
    contentElement.appendChild(textElement);
    messageElement.appendChild(contentElement);
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Switch to chat tab
    document.querySelector('.nav-item[data-page="chat"]').click();
}

/**
 * Fetch system status
 */
function fetchSystemStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok' && data.system) {
                updateDashboard(data.system);
            } else {
                console.error('Error fetching system status:', data);
            }
        })
        .catch(error => {
            console.error('Error fetching system status:', error);
        });
}

/**
 * Update dashboard with system status
 */
function updateDashboard(systemData) {
    // Update system version
    document.getElementById('system-version').textContent = systemData.version || '-.-.-';
    
    // Update uptime
    const uptime = systemData.uptime || 0;
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    const seconds = uptime % 60;
    document.getElementById('system-uptime').textContent = 
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Update memory count
    document.getElementById('memory-count').textContent = 
        systemData.memory ? systemData.memory.total_memories : '--';
    
    // Update active brains
    const modules = systemData.modules || {};
    const activeModules = Object.keys(modules).filter(key => modules[key].active).length;
    document.getElementById('active-brains').textContent = activeModules.toString();
    
    // Update brain modules
    const brainModulesGrid = document.getElementById('brain-modules-grid');
    brainModulesGrid.innerHTML = '';
    
    Object.keys(modules).forEach(moduleName => {
        const module = modules[moduleName];
        
        const moduleElement = document.createElement('div');
        moduleElement.className = `brain-module ${module.active ? 'active' : 'inactive'}`;
        
        const moduleHeader = document.createElement('div');
        moduleHeader.className = 'brain-module-header';
        
        const moduleName_el = document.createElement('div');
        moduleName_el.className = 'brain-module-name';
        moduleName_el.textContent = moduleName.charAt(0).toUpperCase() + moduleName.slice(1);
        
        const moduleStatus = document.createElement('div');
        moduleStatus.className = 'brain-module-status';
        moduleStatus.innerHTML = module.active ? 
            '<span class="status-indicator online"></span><span class="status-text">Active</span>' : 
            '<span class="status-indicator offline"></span><span class="status-text">Inactive</span>';
        
        moduleHeader.appendChild(moduleName_el);
        moduleHeader.appendChild(moduleStatus);
        
        const moduleStats = document.createElement('div');
        moduleStats.className = 'brain-module-stats';
        
        const stats = module.stats || {};
        
        const processingCount = document.createElement('div');
        processingCount.className = 'stat-item';
        processingCount.innerHTML = `<div class="stat-label">Processed</div><div class="stat-value">${stats.processing_count || 0}</div>`;
        
        const errorCount = document.createElement('div');
        errorCount.className = 'stat-item';
        errorCount.innerHTML = `<div class="stat-label">Errors</div><div class="stat-value">${stats.error_count || 0}</div>`;
        
        moduleStats.appendChild(processingCount);
        moduleStats.appendChild(errorCount);
        
        const moduleLastUsed = document.createElement('div');
        moduleLastUsed.className = 'brain-module-last-used';
        
        const lastUsed = module.last_used ? new Date(module.last_used * 1000) : null;
        moduleLastUsed.innerHTML = `<div class="last-used-label">Last Used</div><div class="last-used-value">${lastUsed ? formatTimeAgo(lastUsed) : 'Never'}</div>`;
        
        moduleElement.appendChild(moduleHeader);
        moduleElement.appendChild(moduleStats);
        moduleElement.appendChild(moduleLastUsed);
        
        brainModulesGrid.appendChild(moduleElement);
    });
}

/**
 * Format time ago
 */
function formatTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return `${diffInSeconds} sec ago`;
    }
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
        return `${diffInMinutes} min ago`;
    }
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
        return `${diffInHours} hr ago`;
    }
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
}