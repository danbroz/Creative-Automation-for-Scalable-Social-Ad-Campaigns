/**
 * API Client Module
 * ==================
 * 
 * Comprehensive API client for the Creative Automation Platform.
 * Provides methods to interact with all backend endpoints.
 * 
 * Features:
 * - Campaign creation and management
 * - Status tracking and polling
 * - Asset management
 * - Statistics and analytics
 * - Error handling with retries
 * 
 * Usage:
 *   const api = new APIClient();
 *   const campaign = await api.createCampaign(briefData);
 *   const status = await api.getCampaignStatus(campaign.campaign_id);
 */

class APIClient {
    /**
     * Initialize API client
     * @param {string} baseURL - Base URL for API (default: current origin)
     */
    constructor(baseURL = window.location.origin) {
        this.baseURL = baseURL;
        this.apiKeyHeader = 'X-API-Key';
        this.apiKey = localStorage.getItem('api_key') || null;
    }

    /**
     * Make HTTP request with error handling
     * @private
     * @param {string} endpoint - API endpoint path
     * @param {object} options - Fetch options
     * @returns {Promise} Response data
     */
    async _request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        // Add headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add API key if configured
        if (this.apiKey) {
            headers[this.apiKeyHeader] = this.apiKey;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                
                try {
                    const error = await response.json();
                    console.error('API Error Response:', error);
                    
                    // Handle different error formats
                    if (typeof error.detail === 'string') {
                        errorMessage = error.detail;
                    } else if (Array.isArray(error.detail)) {
                        // FastAPI validation errors are arrays
                        errorMessage = error.detail.map(err => {
                            if (err.msg) return `${err.loc?.join(' → ') || 'Field'}: ${err.msg}`;
                            return JSON.stringify(err);
                        }).join('; ');
                    } else if (typeof error.detail === 'object') {
                        errorMessage = JSON.stringify(error.detail);
                    } else if (error.message) {
                        errorMessage = error.message;
                    }
                } catch (parseError) {
                    // If response isn't JSON, use status text
                    console.error('Could not parse error response:', parseError);
                }
                
                throw new Error(errorMessage);
            }
            
            // Return JSON response
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * Set API key for authentication
     * @param {string} apiKey - API key
     */
    setApiKey(apiKey) {
        this.apiKey = apiKey;
        localStorage.setItem('api_key', apiKey);
    }

    /**
     * Clear API key
     */
    clearApiKey() {
        this.apiKey = null;
        localStorage.removeItem('api_key');
    }

    // ========================================================================
    // Campaign Endpoints
    // ========================================================================

    /**
     * Create a new campaign
     * @param {object} briefData - Campaign brief data
     * @param {Array} briefData.products - List of products (minimum 2)
     * @param {string} briefData.target_region - Target region
     * @param {string} briefData.target_audience - Target audience
     * @param {string} briefData.campaign_message - Campaign message (max 500 chars)
     * @param {string} briefData.language - Language code (default: 'en')
     * @returns {Promise<object>} Campaign response with ID and status
     */
    async createCampaign(briefData) {
        return await this._request('/api/v1/campaigns/create', {
            method: 'POST',
            body: JSON.stringify(briefData)
        });
    }

    /**
     * Get campaign status and details
     * @param {string} campaignId - Campaign ID
     * @returns {Promise<object>} Campaign status object
     */
    async getCampaignStatus(campaignId) {
        return await this._request(`/api/v1/campaigns/${campaignId}`);
    }

    /**
     * Get campaign assets
     * @param {string} campaignId - Campaign ID
     * @returns {Promise<object>} Assets list
     */
    async getCampaignAssets(campaignId) {
        return await this._request(`/api/v1/campaigns/${campaignId}/assets`);
    }

    /**
     * Create batch campaigns from files
     * @param {FileList} files - Campaign brief JSON files
     * @returns {Promise<object>} Batch creation response
     */
    async createBatchCampaigns(files) {
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });
        
        const url = `${this.baseURL}/api/v1/campaigns/batch`;
        const headers = {};
        if (this.apiKey) {
            headers[this.apiKeyHeader] = this.apiKey;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    }

    // ========================================================================
    // Statistics and Analytics Endpoints
    // ========================================================================

    /**
     * Get platform statistics
     * @returns {Promise<object>} Statistics object
     */
    async getStatistics() {
        return await this._request('/api/v1/stats');
    }

    /**
     * Get health status
     * @returns {Promise<object>} Health status
     */
    async getHealth() {
        return await this._request('/api/v1/health');
    }

    // ========================================================================
    // Polling and Real-time Updates
    // ========================================================================

    /**
     * Poll campaign status until completion
     * @param {string} campaignId - Campaign ID
     * @param {function} onUpdate - Callback for status updates
     * @param {number} interval - Polling interval in ms (default: 2000)
     * @returns {Promise<object>} Final campaign status
     */
    async pollCampaignStatus(campaignId, onUpdate, interval = 2000) {
        return new Promise((resolve, reject) => {
            const poll = async () => {
                try {
                    const status = await this.getCampaignStatus(campaignId);
                    
                    // Call update callback
                    if (onUpdate) {
                        onUpdate(status);
                    }
                    
                    // Check if completed or failed
                    if (status.status === 'completed') {
                        resolve(status);
                    } else if (status.status === 'failed') {
                        reject(new Error(status.error || 'Campaign failed'));
                    } else {
                        // Continue polling
                        setTimeout(poll, interval);
                    }
                    
                } catch (error) {
                    reject(error);
                }
            };
            
            poll();
        });
    }

    // ========================================================================
    // Helper Methods
    // ========================================================================

    /**
     * Validate campaign brief data
     * @param {object} briefData - Campaign brief
     * @returns {object} Validation result {valid: boolean, errors: Array}
     */
    validateBrief(briefData) {
        const errors = [];
        
        // Check products
        if (!briefData.products || !Array.isArray(briefData.products)) {
            errors.push('Products must be an array');
        } else if (briefData.products.length < 1) {
            errors.push('At least 1 product is required');
        } else {
            briefData.products.forEach((product, idx) => {
                if (!product.name || product.name.trim() === '') {
                    errors.push(`Product ${idx + 1} must have a name`);
                }
            });
        }
        
        // Check required fields
        if (!briefData.target_region || briefData.target_region.trim() === '') {
            errors.push('Target region is required');
        }
        
        if (!briefData.target_audience || briefData.target_audience.trim() === '') {
            errors.push('Target audience is required');
        }
        
        if (!briefData.campaign_message || briefData.campaign_message.trim() === '') {
            errors.push('Campaign message is required');
        } else if (briefData.campaign_message.length > 500) {
            errors.push('Campaign message must be 500 characters or less');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    }
}

// Export for use in other modules
window.APIClient = APIClient;

