/**
 * Universal Loading System for Vector Space
 * Automatically handles form submissions, file uploads, and async operations
 */

class LoadingManager {
    constructor() {
        this.overlay = null;
        this.init();
    }

    init() {
        this.createOverlay();
        this.attachFormHandlers();
        this.attachFileUploadHandlers();
    }

    createOverlay() {
        // Create global page loading overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'page-loading-overlay';
        this.overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading<span class="loading-dots"></span></div>
            <div class="loading-progress">
                <div class="loading-progress-bar"></div>
            </div>
        `;
        document.body.appendChild(this.overlay);
    }

    show(message = 'Loading') {
        const textEl = this.overlay.querySelector('.loading-text');
        if (textEl) {
            textEl.innerHTML = message + '<span class="loading-dots"></span>';
        }
        this.overlay.classList.add('active');
    }

    hide() {
        this.overlay.classList.remove('active');
    }

    setProgress(percent) {
        const progressBar = this.overlay.querySelector('.loading-progress-bar');
        if (progressBar) {
            progressBar.style.width = percent + '%';
        }
    }

    attachFormHandlers() {
        // Auto-handle all form submissions
        document.addEventListener('submit', (e) => {
            const form = e.target;

            // Skip if form has data-no-loading attribute
            if (form.hasAttribute('data-no-loading')) return;

            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                this.setButtonLoading(submitBtn, true);
            }

            // Check if it's a file upload form
            const hasFileInput = form.querySelector('input[type="file"]');
            if (hasFileInput && hasFileInput.files.length > 0) {
                this.show('Uploading files');
            } else {
                this.show('Processing');
            }
        });
    }

    attachFileUploadHandlers() {
        // Handle file upload progress
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const files = e.target.files;
                if (files.length > 0) {
                    const totalSize = Array.from(files).reduce((sum, file) => sum + file.size, 0);
                    const sizeMB = (totalSize / (1024 * 1024)).toFixed(2);
                    console.log(`Selected ${files.length} file(s), total size: ${sizeMB}MB`);

                    // Show file info in upload zone if exists
                    const uploadZone = input.closest('.upload-zone');
                    if (uploadZone) {
                        const uploadText = uploadZone.querySelector('.upload-text');
                        if (uploadText) {
                            uploadText.textContent = `${files.length} file(s) selected (${sizeMB}MB)`;
                        }
                    }
                }
            });
        });
    }

    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.classList.add('loading');
            button.setAttribute('data-original-text', button.innerHTML);
            button.innerHTML = '<span>Processing...</span>';
        } else {
            button.disabled = false;
            button.classList.remove('loading');
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.innerHTML = originalText;
            }
        }
    }

    // Form-specific loading overlay
    static showFormLoading(form) {
        let overlay = form.querySelector('.form-loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'form-loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner"></div>
                <div class="loading-text">Processing<span class="loading-dots"></span></div>
            `;
            form.style.position = 'relative';
            form.appendChild(overlay);
        }
        overlay.classList.add('active');
    }

    static hideFormLoading(form) {
        const overlay = form.querySelector('.form-loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    // Upload-specific loading
    static showUploadLoading(container, message = 'Uploading') {
        let overlay = container.querySelector('.upload-loading');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'upload-loading';
            overlay.innerHTML = `
                <div class="upload-progress-circle">
                    <div class="upload-progress-percent">0%</div>
                </div>
                <div class="upload-status-text">${message}</div>
                <div class="upload-status-detail">Please wait...</div>
            `;
            container.style.position = 'relative';
            container.appendChild(overlay);
        }
        overlay.classList.add('active');
        return overlay;
    }

    static updateUploadProgress(container, percent, status = null) {
        const overlay = container.querySelector('.upload-loading');
        if (overlay) {
            const percentEl = overlay.querySelector('.upload-progress-percent');
            if (percentEl) percentEl.textContent = percent + '%';

            if (status) {
                const statusEl = overlay.querySelector('.upload-status-detail');
                if (statusEl) statusEl.textContent = status;
            }
        }
    }

    static hideUploadLoading(container) {
        const overlay = container.querySelector('.upload-loading');
        if (overlay) {
            overlay.classList.remove('active');
            setTimeout(() => overlay.remove(), 300);
        }
    }

    // Payment processing indicator
    static showPaymentProcessing(message = 'Processing payment') {
        const existingOverlay = document.querySelector('.payment-processing-overlay');
        if (existingOverlay) return;

        const overlay = document.createElement('div');
        overlay.className = 'page-loading-overlay payment-processing-overlay active';
        overlay.innerHTML = `
            <div class="payment-processing">
                <div class="payment-processing-icon"></div>
                <div class="payment-processing-text">${message}</div>
                <div class="payment-processing-detail">Please do not close this window</div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    static hidePaymentProcessing() {
        const overlay = document.querySelector('.payment-processing-overlay');
        if (overlay) {
            overlay.classList.remove('active');
            setTimeout(() => overlay.remove(), 300);
        }
    }

    // Search loading indicator
    static showSearchLoading(container) {
        const indicator = document.createElement('div');
        indicator.className = 'search-loading';
        indicator.innerHTML = `
            <span class="spinner-inline"></span>
            <span>Searching...</span>
        `;
        container.appendChild(indicator);
        return indicator;
    }
}

// Initialize on page load
let loadingManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadingManager = new LoadingManager();
    });
} else {
    loadingManager = new LoadingManager();
}

// Export for use in other scripts
window.LoadingManager = LoadingManager;
window.loadingManager = loadingManager;