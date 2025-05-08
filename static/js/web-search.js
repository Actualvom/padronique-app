/**
 * Web Search Module for Padronique AI Companion
 * Handles web searches and result processing
 */

class WebSearch {
    constructor() {
        // DOM Elements
        this.webSearchBtn = document.getElementById('webSearchBtn');
        this.closeWebSearchBtn = document.getElementById('closeWebSearchBtn');
        this.executeWebSearchBtn = document.getElementById('executeWebSearchBtn');
        this.useWebSearchResultsBtn = document.getElementById('useWebSearchResultsBtn');
        this.webSearchInput = document.getElementById('webSearchInput');
        this.webSearchContainer = document.getElementById('webSearchContainer');
        this.webSearchResults = document.getElementById('webSearchResults');
        
        // State
        this.currentSearchQuery = '';
        this.searchResults = [];
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize web search interface
     */
    init() {
        // Attach event listeners
        this.webSearchBtn.addEventListener('click', () => this.showWebSearch());
        this.closeWebSearchBtn.addEventListener('click', () => this.hideWebSearch());
        this.executeWebSearchBtn.addEventListener('click', () => this.performSearch());
        this.useWebSearchResultsBtn.addEventListener('click', () => this.useSearchResults());
        
        // Search on Enter key
        this.webSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
    }
    
    /**
     * Show web search interface
     */
    showWebSearch() {
        this.webSearchContainer.style.display = 'block';
        this.webSearchInput.focus();
        
        // Hide other containers
        document.querySelector('.voice-recording-container').style.display = 'none';
        document.getElementById('cameraContainer').style.display = 'none';
    }
    
    /**
     * Hide web search interface
     */
    hideWebSearch() {
        this.webSearchContainer.style.display = 'none';
        this.webSearchInput.value = '';
        this.resetResults();
    }
    
    /**
     * Reset search results
     */
    resetResults() {
        this.webSearchResults.innerHTML = `
            <div class="text-center p-3">
                <i class="fas fa-search fa-2x mb-3"></i>
                <p>Enter a search term to find information on the web</p>
            </div>
        `;
        this.searchResults = [];
        this.useWebSearchResultsBtn.disabled = true;
    }
    
    /**
     * Perform web search
     */
    async performSearch() {
        const query = this.webSearchInput.value.trim();
        
        if (!query) {
            return;
        }
        
        this.currentSearchQuery = query;
        this.webSearchResults.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Searching for "${this.escapeHtml(query)}"...</p>
            </div>
        `;
        
        try {
            const response = await fetch(`/api/web-search?query=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'ok' && data.results && data.results.length > 0) {
                this.displaySearchResults(data.results);
                this.searchResults = data.results;
                this.useWebSearchResultsBtn.disabled = false;
            } else {
                this.displayNoResults();
            }
        } catch (error) {
            console.error('Error performing web search:', error);
            this.displayError();
        }
    }
    
    /**
     * Display search results
     */
    displaySearchResults(results) {
        this.webSearchResults.innerHTML = '';
        
        results.forEach(result => {
            const resultElement = document.createElement('div');
            resultElement.className = 'search-result-item';
            
            resultElement.innerHTML = `
                <div class="search-result-title">
                    <a href="${this.escapeHtml(result.url)}" target="_blank">
                        ${this.escapeHtml(result.title)}
                    </a>
                </div>
                <div class="search-result-url">${this.escapeHtml(result.url)}</div>
                <div class="search-result-snippet">${this.escapeHtml(result.snippet)}</div>
            `;
            
            this.webSearchResults.appendChild(resultElement);
        });
    }
    
    /**
     * Display no results message
     */
    displayNoResults() {
        this.webSearchResults.innerHTML = `
            <div class="text-center p-3">
                <i class="fas fa-search fa-2x mb-3"></i>
                <p>No results found for "${this.escapeHtml(this.currentSearchQuery)}"</p>
            </div>
        `;
        this.searchResults = [];
        this.useWebSearchResultsBtn.disabled = true;
    }
    
    /**
     * Display error message
     */
    displayError() {
        this.webSearchResults.innerHTML = `
            <div class="text-center p-3">
                <i class="fas fa-exclamation-triangle fa-2x mb-3 text-danger"></i>
                <p>Error performing search. Please try again.</p>
            </div>
        `;
        this.searchResults = [];
        this.useWebSearchResultsBtn.disabled = true;
    }
    
    /**
     * Use search results in conversation
     */
    useSearchResults() {
        if (this.searchResults.length === 0) {
            return;
        }
        
        // Format search results
        const formattedResults = this.formatSearchResults();
        
        // Reset and hide web search UI
        this.hideWebSearch();
        
        // Send to chat
        if (window.sendMessage) {
            window.sendMessage(formattedResults);
        } else {
            // Fallback if sendMessage is not globally available
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            
            messageInput.value = formattedResults;
            sendBtn.click();
        }
    }
    
    /**
     * Format search results for conversation
     */
    formatSearchResults() {
        let formattedResults = `Please analyze these web search results for "${this.escapeHtml(this.currentSearchQuery)}":\n\n`;
        
        this.searchResults.forEach((result, index) => {
            formattedResults += `Result ${index + 1}: ${result.title}\n`;
            formattedResults += `URL: ${result.url}\n`;
            formattedResults += `${result.snippet}\n\n`;
        });
        
        return formattedResults;
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
window.WebSearch = WebSearch;