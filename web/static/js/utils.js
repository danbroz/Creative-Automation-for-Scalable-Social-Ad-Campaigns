/**
 * Utility Functions Module
 * =========================
 * 
 * Common utility functions used throughout the application.
 * Provides helpers for formatting, DOM manipulation, and UI components.
 * 
 * Functions:
 * - formatDate: Format dates for display
 * - formatCurrency: Format currency values
 * - showToast: Display toast notifications
 * - showLoading: Show/hide loading indicators
 * - formatFileSize: Format bytes to readable format
 * - copyToClipboard: Copy text to clipboard
 */

/**
 * Utility class with static helper methods
 */
class Utils {
    /**
     * Format date to readable string
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date string
     */
    static formatDate(date) {
        if (!date) return '-';
        
        const d = new Date(date);
        const now = new Date();
        
        // Handle invalid dates
        if (isNaN(d.getTime())) return 'Invalid date';
        
        const diffMs = now - d;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        // Relative time for recent dates
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        
        // Absolute date for older items
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Format currency value
     * @param {number} amount - Amount to format
     * @param {string} currency - Currency code (default: 'USD')
     * @returns {string} Formatted currency string
     */
    static formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    /**
     * Format file size to readable format
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted size (e.g., "1.5 MB")
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Display duration in ms (default: 3000)
     */
    static showToast(message, type = 'info', duration = 3000) {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Add to DOM
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * Show loading indicator
     * @param {boolean} show - Show or hide loading
     * @param {string} message - Loading message (optional)
     */
    static showLoading(show, message = 'Loading...') {
        let loader = document.getElementById('global-loader');
        
        if (show) {
            if (!loader) {
                loader = document.createElement('div');
                loader.id = 'global-loader';
                loader.className = 'global-loader';
                loader.innerHTML = `
                    <div class="loader-content">
                        <div class="spinner"></div>
                        <p class="loader-message">${message}</p>
                    </div>
                `;
                document.body.appendChild(loader);
            } else {
                loader.querySelector('.loader-message').textContent = message;
            }
            loader.classList.add('show');
        } else {
            if (loader) {
                loader.classList.remove('show');
            }
        }
    }

    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} Success status
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard!', 'success');
            return true;
        } catch (error) {
            console.error('Failed to copy:', error);
            this.showToast('Failed to copy', 'error');
            return false;
        }
    }

    /**
     * Get status badge HTML
     * @param {string} status - Status value
     * @returns {string} HTML for status badge
     */
    static getStatusBadge(status) {
        const statusMap = {
            'queued': { class: 'warning', icon: '⏳', text: 'Queued' },
            'pending': { class: 'warning', icon: '⏳', text: 'Pending' },
            'in_progress': { class: 'info', icon: '⚙️', text: 'Processing' },
            'completed': { class: 'success', icon: '✓', text: 'Completed' },
            'failed': { class: 'error', icon: '✗', text: 'Failed' },
            'cancelled': { class: 'secondary', icon: '⊘', text: 'Cancelled' }
        };
        
        const config = statusMap[status] || statusMap['pending'];
        
        return `<span class="badge badge-${config.class}">
            <span class="badge-icon">${config.icon}</span>
            <span class="badge-text">${config.text}</span>
        </span>`;
    }

    /**
     * Debounce function calls
     * @param {function} func - Function to debounce
     * @param {number} wait - Wait time in ms
     * @returns {function} Debounced function
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Truncate text to maximum length
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text with ellipsis
     */
    static truncate(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * Get language flag emoji
     * @param {string} languageCode - Language code (e.g., 'en', 'es')
     * @returns {string} Flag emoji
     */
    static getLanguageFlag(languageCode) {
        const flags = {
            'en': '🇺🇸',
            'es': '🇪🇸',
            'fr': '🇫🇷',
            'de': '🇩🇪',
            'it': '🇮🇹',
            'pt': '🇵🇹',
            'zh': '🇨🇳',
            'ja': '🇯🇵',
            'ko': '🇰🇷'
        };
        return flags[languageCode] || '🌐';
    }

    /**
     * Format duration in seconds to readable format
     * @param {number} seconds - Duration in seconds
     * @returns {string} Formatted duration
     */
    static formatDuration(seconds) {
        if (seconds < 60) return `${Math.round(seconds)}s`;
        if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
        return `${Math.round(seconds / 3600)}h`;
    }

    /**
     * Generate unique ID
     * @returns {string} Unique ID
     */
    static generateId() {
        return 'id-' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Sanitize HTML to prevent XSS
     * @param {string} html - HTML string
     * @returns {string} Sanitized HTML
     */
    static sanitizeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
}

// Export for global use
window.Utils = Utils;

