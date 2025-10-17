/**
 * Dashboard Module
 * =================
 * 
 * Handles dashboard page functionality including:
 * - Loading and displaying statistics
 * - Recent campaigns list
 * - Real-time updates
 * - Quick actions
 * 
 * Dependencies: api.js, utils.js
 */

/**
 * Dashboard controller class
 */
class Dashboard {
    constructor() {
        this.api = new APIClient();
        this.refreshInterval = null;
        this.init();
    }

    /**
     * Initialize dashboard
     */
    async init() {
        try {
            // Load initial data
            await this.loadStatistics();
            
            // Setup auto-refresh every 30 seconds
            this.refreshInterval = setInterval(() => {
                this.loadStatistics();
            }, 30000);
            
            // Setup event listeners
            this.setupEventListeners();
            
        } catch (error) {
            console.error('Dashboard initialization error:', error);
            Utils.showToast('Failed to load dashboard', 'error');
        }
    }

    /**
     * Load and display statistics
     */
    async loadStatistics() {
        try {
            const stats = await this.api.getStatistics();
            
            // Update metrics cards
            this.updateMetricsCards(stats);
            
            // Update recent campaigns (if data available)
            if (stats.recent_campaigns) {
                this.updateRecentCampaigns(stats.recent_campaigns);
            }
            
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    /**
     * Update metrics cards with statistics data
     * @param {object} stats - Statistics object
     */
    updateMetricsCards(stats) {
        // Total campaigns
        const totalEl = document.getElementById('metric-total-campaigns');
        if (totalEl) {
            this.animateNumber(totalEl, stats.total || 0);
        }
        
        // Pending campaigns
        const pendingEl = document.getElementById('metric-pending');
        if (pendingEl) {
            this.animateNumber(pendingEl, stats.pending || 0);
        }
        
        // Completed campaigns
        const completedEl = document.getElementById('metric-completed');
        if (completedEl) {
            this.animateNumber(completedEl, stats.completed || 0);
        }
        
        // In progress
        const inProgressEl = document.getElementById('metric-in-progress');
        if (inProgressEl) {
            this.animateNumber(inProgressEl, stats.in_progress || 0);
        }
    }

    /**
     * Animate number counting up
     * @param {HTMLElement} element - Element to update
     * @param {number} endValue - Target value
     */
    animateNumber(element, endValue) {
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;  // 1 second animation
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (easeOutCubic)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.floor(startValue + (endValue - startValue) * easeOut);
            
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * Update recent campaigns list
     * @param {Array} campaigns - Array of campaign objects
     */
    updateRecentCampaigns(campaigns) {
        const tableBody = document.getElementById('recent-campaigns-body');
        if (!tableBody) return;
        
        if (!campaigns || campaigns.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-gray-500 py-8">
                        No campaigns yet. Create your first campaign!
                    </td>
                </tr>
            `;
            return;
        }
        
        // Build table rows
        const rows = campaigns.map(campaign => `
            <tr class="hover:bg-gray-50 transition-colors cursor-pointer" 
                onclick="window.location.href='campaign-detail.html?id=${campaign.job_id}'">
                <td class="px-6 py-4">
                    <div class="font-medium text-gray-900">${Utils.sanitizeHTML(campaign.brief_path.split('/').pop().replace('.json', ''))}</div>
                    <div class="text-sm text-gray-500">${Utils.formatDate(campaign.created_at)}</div>
                </td>
                <td class="px-6 py-4">
                    ${Utils.getStatusBadge(campaign.status)}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                    ${campaign.started_at ? Utils.formatDate(campaign.started_at) : '-'}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                    ${campaign.completed_at ? Utils.formatDate(campaign.completed_at) : '-'}
                </td>
                <td class="px-6 py-4 text-right">
                    <button class="text-primary hover:text-primary-dark" 
                            onclick="event.stopPropagation(); viewCampaign('${campaign.job_id}')">
                        View →
                    </button>
                </td>
            </tr>
        `).join('');
        
        tableBody.innerHTML = rows;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Create campaign button
        const createBtn = document.getElementById('btn-create-campaign');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                window.location.href = 'create-campaign.html';
            });
        }
        
        // View all campaigns button
        const viewAllBtn = document.getElementById('btn-view-all');
        if (viewAllBtn) {
            viewAllBtn.addEventListener('click', () => {
                window.location.href = 'campaigns.html';
            });
        }
        
        // Analytics button
        const analyticsBtn = document.getElementById('btn-analytics');
        if (analyticsBtn) {
            analyticsBtn.addEventListener('click', () => {
                window.location.href = 'analytics.html';
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('btn-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                await this.loadStatistics();
                Utils.showToast('Dashboard refreshed', 'success');
            });
        }
    }

    /**
     * Cleanup on page unload
     */
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

/**
 * View campaign details
 * @param {string} campaignId - Campaign ID
 */
function viewCampaign(campaignId) {
    window.location.href = `campaign-detail.html?id=${campaignId}`;
}

// Initialize dashboard when DOM is ready
let dashboardInstance;

document.addEventListener('DOMContentLoaded', () => {
    dashboardInstance = new Dashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboardInstance) {
        dashboardInstance.destroy();
    }
});

