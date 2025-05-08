/**
 * Padronique API Client
 * 
 * Handles communication with the backend API
 */

class PadroniqueAPI {
    constructor() {
        this.baseUrl = '/api';
    }
    
    /**
     * Process user input
     * 
     * @param {string} message - User message
     * @param {string} type - Message type (text, image, etc.)
     * @returns {Promise} - API response
     */
    processInput(message, type = 'text') {
        return this._request('/process', 'POST', {
            content: message,
            type: type
        });
    }
    
    /**
     * Get system status
     * 
     * @returns {Promise} - API response
     */
    getStatus() {
        return this._request('/status', 'GET');
    }
    
    /**
     * Reset system
     * 
     * @param {string} type - Reset type (chat_history, full_system)
     * @returns {Promise} - API response
     */
    resetSystem(type = 'full_system') {
        return this._request('/reset', 'POST', {
            type: type
        });
    }
    
    /**
     * Get memories
     * 
     * @param {string} query - Search query
     * @param {string} tags - Tags to filter by
     * @param {number} limit - Maximum number of memories to return
     * @returns {Promise} - API response
     */
    getMemories(query = '', tags = '', limit = 10) {
        const params = new URLSearchParams();
        
        if (query) {
            params.append('query', query);
        }
        
        if (tags) {
            params.append('tags', tags);
        }
        
        params.append('limit', limit);
        
        return this._request(`/memory?${params.toString()}`, 'GET');
    }
    
    /**
     * Get memory by ID
     * 
     * @param {string} memoryId - Memory ID
     * @returns {Promise} - API response
     */
    getMemory(memoryId) {
        return this._request(`/memory/${memoryId}`, 'GET');
    }
    
    /**
     * Create memory
     * 
     * @param {Object} data - Memory data
     * @param {Array} tags - Memory tags
     * @returns {Promise} - API response
     */
    createMemory(data, tags = []) {
        const memoryData = { ...data, tags };
        return this._request('/memory', 'POST', memoryData);
    }
    
    /**
     * Delete memory
     * 
     * @param {string} memoryId - Memory ID
     * @returns {Promise} - API response
     */
    deleteMemory(memoryId) {
        return this._request(`/memory/${memoryId}`, 'DELETE');
    }
    
    /**
     * Add tags to memory
     * 
     * @param {string} memoryId - Memory ID
     * @param {Array} tags - Tags to add
     * @returns {Promise} - API response
     */
    addTags(memoryId, tags) {
        return this._request(`/memory/${memoryId}/tags`, 'POST', {
            tags: tags
        });
    }
    
    /**
     * Provide feedback
     * 
     * @param {string} interactionId - Interaction ID
     * @param {Object} feedback - Feedback data
     * @returns {Promise} - API response
     */
    provideFeedback(interactionId, feedback) {
        return this._request('/feedback', 'POST', {
            interaction_id: interactionId,
            feedback: feedback
        });
    }
    
    /**
     * Get brain modules info
     * 
     * @returns {Promise} - API response
     */
    getModules() {
        return this._request('/modules', 'GET');
    }
    
    /**
     * Get module info
     * 
     * @param {string} moduleName - Module name
     * @returns {Promise} - API response
     */
    getModuleInfo(moduleName) {
        return this._request(`/modules/${moduleName}`, 'GET');
    }
    
    /**
     * Toggle module
     * 
     * @param {string} moduleName - Module name
     * @param {boolean} active - Active state
     * @returns {Promise} - API response
     */
    toggleModule(moduleName, active) {
        return this._request(`/modules/${moduleName}`, 'POST', {
            active: active
        });
    }
    
    /**
     * Update module config
     * 
     * @param {string} moduleName - Module name
     * @param {Object} config - Module configuration
     * @returns {Promise} - API response
     */
    updateModuleConfig(moduleName, config) {
        return this._request(`/modules/${moduleName}/config`, 'POST', {
            config: config
        });
    }
    
    /**
     * Make API request
     * 
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {Object} data - Request data
     * @returns {Promise} - Fetch promise
     * @private
     */
    _request(endpoint, method, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
                }
                return response.json();
            });
    }
}

// Create global API instance
const padroniqueAPI = new PadroniqueAPI();