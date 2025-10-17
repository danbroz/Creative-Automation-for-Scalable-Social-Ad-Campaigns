/**
 * Campaign Form Module
 * =====================
 * 
 * Handles multi-step campaign creation form with validation,
 * real-time feedback, and submission to API.
 * 
 * Form Steps:
 * 1. Products - Add 2+ products with names and descriptions
 * 2. Targeting - Region, audience, language
 * 3. Message - Campaign message with preview
 * 4. Review - Summary and submit
 */

class CampaignForm {
    constructor() {
        this.api = new APIClient();
        this.currentStep = 1;
        this.totalSteps = 4;
        this.formData = {
            campaign_name: '',
            products: [{name: '', description: ''}],
            target_region: '',
            target_audience: '',
            campaign_message: '',
            language: 'en'
        };
        
        this.init();
    }

    /**
     * Initialize form
     */
    init() {
        this.setupEventListeners();
        this.loadDraft(); // Load saved draft from localStorage
        this.showStep(1);
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Next button
        const nextBtn = document.getElementById('btn-next');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }
        
        // Previous button
        const prevBtn = document.getElementById('btn-prev');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousStep());
        }
        
        // Submit button
        const submitBtn = document.getElementById('btn-submit');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitForm());
        }
        
        // Add product button
        const addProductBtn = document.getElementById('btn-add-product');
        if (addProductBtn) {
            addProductBtn.addEventListener('click', () => this.addProduct());
        }
        
        // Auto-save on input change
        document.addEventListener('input', Utils.debounce(() => {
            this.saveDraft();
        }, 1000));
    }

    /**
     * Show specific step
     * @param {number} step - Step number (1-4)
     */
    showStep(step) {
        this.currentStep = step;
        
        // Hide all steps
        for (let i = 1; i <= this.totalSteps; i++) {
            const stepEl = document.getElementById(`step-${i}`);
            if (stepEl) {
                stepEl.classList.add('hidden');
            }
        }
        
        // Show current step
        const currentStepEl = document.getElementById(`step-${step}`);
        if (currentStepEl) {
            currentStepEl.classList.remove('hidden');
        }
        
        // Update step indicator
        this.updateStepIndicator();
        
        // Update buttons
        this.updateButtons();
        
        // Load step data
        this.loadStepData(step);
    }

    /**
     * Go to next step
     */
    nextStep() {
        // Validate current step
        if (!this.validateStep(this.currentStep)) {
            Utils.showToast('Please complete all required fields', 'error');
            return;
        }
        
        // Save current step data
        this.saveStepData(this.currentStep);
        
        // Move to next step
        if (this.currentStep < this.totalSteps) {
            this.showStep(this.currentStep + 1);
        }
    }

    /**
     * Go to previous step
     */
    previousStep() {
        // Save current step data
        this.saveStepData(this.currentStep);
        
        // Move to previous step
        if (this.currentStep > 1) {
            this.showStep(this.currentStep - 1);
        }
    }

    /**
     * Update step indicator UI
     */
    updateStepIndicator() {
        for (let i = 1; i <= this.totalSteps; i++) {
            const indicator = document.getElementById(`indicator-${i}`);
            if (indicator) {
                if (i < this.currentStep) {
                    indicator.className = 'step-indicator completed';
                } else if (i === this.currentStep) {
                    indicator.className = 'step-indicator active';
                } else {
                    indicator.className = 'step-indicator';
                }
            }
        }
    }

    /**
     * Update button states
     */
    updateButtons() {
        const prevBtn = document.getElementById('btn-prev');
        const nextBtn = document.getElementById('btn-next');
        const submitBtn = document.getElementById('btn-submit');
        
        // Previous button
        if (prevBtn) {
            prevBtn.style.display = this.currentStep === 1 ? 'none' : 'inline-block';
        }
        
        // Next button
        if (nextBtn) {
            nextBtn.style.display = this.currentStep === this.totalSteps ? 'none' : 'inline-block';
        }
        
        // Submit button
        if (submitBtn) {
            submitBtn.style.display = this.currentStep === this.totalSteps ? 'inline-block' : 'none';
        }
    }

    /**
     * Validate current step
     * @param {number} step - Step number
     * @returns {boolean} Validation result
     */
    validateStep(step) {
        switch (step) {
            case 1: // Products
                return this.validateProducts();
            case 2: // Targeting
                return this.validateTargeting();
            case 3: // Message
                return this.validateMessage();
            case 4: // Review
                return true; // Review step has no validation
            default:
                return false;
        }
    }

    /**
     * Validate products step
     * @returns {boolean} Validation result
     */
    validateProducts() {
        const products = this.getProducts();
        
        if (products.length < 1) {
            return false;
        }
        
        // Check all products have names
        return products.every(p => p.name && p.name.trim() !== '');
    }

    /**
     * Validate targeting step
     * @returns {boolean} Validation result
     */
    validateTargeting() {
        const region = document.getElementById('target-region')?.value;
        const audience = document.getElementById('target-audience')?.value;
        
        return region && region.trim() !== '' && 
               audience && audience.trim() !== '';
    }

    /**
     * Validate message step
     * @returns {boolean} Validation result
     */
    validateMessage() {
        const message = document.getElementById('campaign-message')?.value;
        
        return message && message.trim() !== '' && message.length <= 500;
    }

    /**
     * Save current step data to formData
     * @param {number} step - Step number
     */
    saveStepData(step) {
        switch (step) {
            case 1:
                this.formData.products = this.getProducts();
                break;
            case 2:
                this.formData.target_region = document.getElementById('target-region')?.value || '';
                this.formData.target_audience = document.getElementById('target-audience')?.value || '';
                this.formData.language = document.getElementById('language-select')?.value || 'en';
                break;
            case 3:
                this.formData.campaign_message = document.getElementById('campaign-message')?.value || '';
                this.formData.campaign_name = document.getElementById('campaign-name')?.value || '';
                break;
        }
    }

    /**
     * Load step data into form fields
     * @param {number} step - Step number
     */
    loadStepData(step) {
        switch (step) {
            case 1:
                this.renderProducts();
                break;
            case 2:
                if (document.getElementById('target-region')) {
                    document.getElementById('target-region').value = this.formData.target_region;
                }
                if (document.getElementById('target-audience')) {
                    document.getElementById('target-audience').value = this.formData.target_audience;
                }
                if (document.getElementById('language-select')) {
                    document.getElementById('language-select').value = this.formData.language;
                }
                break;
            case 3:
                if (document.getElementById('campaign-message')) {
                    document.getElementById('campaign-message').value = this.formData.campaign_message;
                }
                if (document.getElementById('campaign-name')) {
                    document.getElementById('campaign-name').value = this.formData.campaign_name;
                }
                this.updateCharCount();
                break;
            case 4:
                this.renderReview();
                break;
        }
    }

    /**
     * Get products from form
     * @returns {Array} Array of product objects
     */
    getProducts() {
        const products = [];
        const productElements = document.querySelectorAll('.product-item');
        
        productElements.forEach(el => {
            const name = el.querySelector('.product-name')?.value || '';
            const description = el.querySelector('.product-description')?.value || '';
            
            if (name.trim() !== '') {
                products.push({ name, description });
            }
        });
        
        return products;
    }

    /**
     * Render products in the form
     */
    renderProducts() {
        const container = document.getElementById('products-container');
        if (!container) return;
        
        container.innerHTML = this.formData.products.map((product, index) => `
            <div class="product-item bg-gray-50 p-4 rounded-lg mb-4">
                <div class="flex justify-between items-center mb-2">
                    <h4 class="font-medium">Product ${index + 1}</h4>
                    ${index >= 1 ? `<button type="button" class="text-red-600 hover:text-red-700" 
                                           onclick="campaignForm.removeProduct(${index})">Remove</button>` : ''}
                </div>
                <input type="text" class="product-name form-input w-full mb-2" 
                       placeholder="Product Name *" value="${Utils.sanitizeHTML(product.name)}" required>
                <textarea class="product-description form-input w-full" rows="2" 
                          placeholder="Description (optional)">${Utils.sanitizeHTML(product.description)}</textarea>
            </div>
        `).join('');
    }

    /**
     * Add new product
     */
    addProduct() {
        this.formData.products.push({name: '', description: ''});
        this.renderProducts();
    }

    /**
     * Remove product
     * @param {number} index - Product index
     */
    removeProduct(index) {
        if (this.formData.products.length > 1) {
            this.formData.products.splice(index, 1);
            this.renderProducts();
        }
    }

    /**
     * Update character count for campaign message
     */
    updateCharCount() {
        const textarea = document.getElementById('campaign-message');
        const counter = document.getElementById('char-count');
        
        if (textarea && counter) {
            const length = textarea.value.length;
            const maxLength = 500;
            counter.textContent = `${length}/${maxLength}`;
            
            if (length > maxLength) {
                counter.classList.add('text-red-600');
            } else {
                counter.classList.remove('text-red-600');
            }
        }
    }

    /**
     * Render review summary
     */
    renderReview() {
        const reviewContainer = document.getElementById('review-summary');
        if (!reviewContainer) return;
        
        const html = `
            <div class="space-y-6">
                <div class="review-section">
                    <h3 class="font-semibold text-lg mb-2">Products (${this.formData.products.length})</h3>
                    <ul class="list-disc list-inside space-y-1">
                        ${this.formData.products.map(p => `<li>${Utils.sanitizeHTML(p.name)}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="review-section">
                    <h3 class="font-semibold text-lg mb-2">Targeting</h3>
                    <p><strong>Region:</strong> ${Utils.sanitizeHTML(this.formData.target_region)}</p>
                    <p><strong>Audience:</strong> ${Utils.sanitizeHTML(this.formData.target_audience)}</p>
                    <p><strong>Language:</strong> ${Utils.getLanguageFlag(this.formData.language)} ${this.formData.language.toUpperCase()}</p>
                </div>
                
                <div class="review-section">
                    <h3 class="font-semibold text-lg mb-2">Campaign Message</h3>
                    <p class="bg-gray-100 p-4 rounded">${Utils.sanitizeHTML(this.formData.campaign_message)}</p>
                </div>
            </div>
        `;
        
        reviewContainer.innerHTML = html;
    }

    /**
     * Submit form to API
     */
    async submitForm() {
        Utils.showLoading(true, 'Creating campaign...');
        
        try {
            // Save all step data
            this.saveStepData(this.currentStep);
            
            // Validate entire form
            const validation = this.api.validateBrief(this.formData);
            if (!validation.valid) {
                throw new Error(validation.errors.join(', '));
            }
            
            // Submit to API
            const response = await this.api.createCampaign(this.formData);
            
            Utils.showLoading(false);
            Utils.showToast('Campaign created successfully!', 'success');
            
            // Clear draft
            this.clearDraft();
            
            // Redirect to campaign detail page
            setTimeout(() => {
                window.location.href = `campaign-detail.html?id=${response.campaign_id}`;
            }, 1000);
            
        } catch (error) {
            Utils.showLoading(false);
            Utils.showToast(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Save draft to localStorage
     */
    saveDraft() {
        this.saveStepData(this.currentStep);
        localStorage.setItem('campaign_draft', JSON.stringify(this.formData));
    }

    /**
     * Load draft from localStorage
     */
    loadDraft() {
        const draft = localStorage.getItem('campaign_draft');
        if (draft) {
            try {
                this.formData = JSON.parse(draft);
            } catch (error) {
                console.error('Error loading draft:', error);
            }
        }
    }

    /**
     * Clear draft from localStorage
     */
    clearDraft() {
        localStorage.removeItem('campaign_draft');
    }
}

// Initialize form when DOM is ready
let campaignForm;

document.addEventListener('DOMContentLoaded', () => {
    campaignForm = new CampaignForm();
    
    // Character counter for campaign message
    const messageTextarea = document.getElementById('campaign-message');
    if (messageTextarea) {
        messageTextarea.addEventListener('input', () => {
            campaignForm.updateCharCount();
        });
    }
});

