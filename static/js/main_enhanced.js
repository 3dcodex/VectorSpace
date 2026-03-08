/**
 * Vector Space - Enhanced Main JavaScript
 * Modern interactions, animations, and utilities
 */

(function() {
    'use strict';

    // ========================================
    // ENHANCED HEADER SCROLL BEHAVIOR
    // ========================================
    
    class HeaderController {
        constructor() {
            this.header = document.querySelector('.main-header');
            this.lastScroll = 0;
            this.scrollThreshold = 100;
            this.init();
        }

        init() {
            if (!this.header) return;
            
            window.addEventListener('scroll', () => this.handleScroll(), { passive: true });
            this.updateScrollProgress();
        }

        handleScroll() {
            const currentScroll = window.pageYOffset;
            
            // Add scrolled class for styling
            if (currentScroll > 50) {
                this.header.classList.add('scrolled');
            } else {
                this.header.classList.remove('scrolled');
            }

            // Hide/show header based on scroll direction
            if (currentScroll > this.scrollThreshold) {
                if (currentScroll > this.lastScroll) {
                    // Scrolling down
                    this.header.classList.add('scroll-down');
                    this.header.classList.remove('scroll-up');
                } else {
                    // Scrolling up
                    this.header.classList.remove('scroll-down');
                    this.header.classList.add('scroll-up');
                }
            }
            
            this.lastScroll = currentScroll;
            this.updateScrollProgress();
        }

        updateScrollProgress() {
            const scrollProgress = document.getElementById('scrollProgress');
            if (scrollProgress) {
                const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                const scrolled = (window.pageYOffset / windowHeight) * 100;
                scrollProgress.style.width = scrolled + '%';
            }
        }
    }

    // ========================================
    // MOBILE MENU CONTROLLER
    // ========================================
    
    class MobileMenuController {
        constructor() {
            this.toggle = document.getElementById('mobileMenuToggle');
            this.menu = document.getElementById('mobileMenu');
            this.init();
        }

        init() {
            if (!this.toggle || !this.menu) return;
            
            this.toggle.addEventListener('click', () => this.toggleMenu());
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!this.toggle.contains(e.target) && !this.menu.contains(e.target)) {
                    this.closeMenu();
                }
            });

            // Close menu on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeMenu();
                }
            });
        }

        toggleMenu() {
            this.menu.classList.toggle('open');
            this.toggle.classList.toggle('active');
            document.body.style.overflow = this.menu.classList.contains('open') ? 'hidden' : '';
        }

        closeMenu() {
            this.menu.classList.remove('open');
            this.toggle.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // ========================================
    // USER DROPDOWN CONTROLLER
    // ========================================
    
    class UserDropdownController {
        constructor() {
            this.userMenu = document.querySelector('.user-menu');
            this.init();
        }

        init() {
            if (!this.userMenu) return;
            
            const userAvatar = this.userMenu.querySelector('.user-avatar');
            if (!userAvatar) return;

            userAvatar.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
            
            document.addEventListener('click', () => {
                this.closeDropdown();
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeDropdown();
                }
            });
        }

        toggleDropdown() {
            this.userMenu.classList.toggle('active');
        }

        closeDropdown() {
            this.userMenu.classList.remove('active');
        }
    }

    // ========================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ========================================
    
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const headerOffset = 80;
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ========================================
    // INTERSECTION OBSERVER FOR ANIMATIONS
    // ========================================
    
    class AnimationObserver {
        constructor() {
            this.options = {
                threshold: 0.1,
                rootMargin: '0px 0px -100px 0px'
            };
            this.init();
        }

        init() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                        observer.unobserve(entry.target);
                    }
                });
            }, this.options);

            // Observe elements with animate-on-scroll class
            document.querySelectorAll('.animate-on-scroll').forEach(el => {
                observer.observe(el);
            });

            // Observe cards and sections
            document.querySelectorAll('.feature-card, .content-card, .hero-stat-card, .step').forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(30px)';
                el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(el);
            });
        }
    }

    // ========================================
    // TOAST NOTIFICATION SYSTEM
    // ========================================
    
    class ToastNotification {
        constructor() {
            this.container = this.createContainer();
        }

        createContainer() {
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.style.cssText = `
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    z-index: 10000;
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                `;
                document.body.appendChild(container);
            }
            return container;
        }

        show(message, type = 'info', duration = 3000) {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.style.cssText = `
                padding: 1rem 1.5rem;
                background: rgba(10, 14, 39, 0.95);
                backdrop-filter: blur(20px);
                border: 1px solid ${this.getBorderColor(type)};
                border-radius: 0.5rem;
                color: white;
                font-weight: 500;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                opacity: 0;
                transform: translateX(100px);
                transition: all 0.3s ease;
                max-width: 350px;
            `;
            toast.textContent = message;
            
            this.container.appendChild(toast);
            
            // Trigger animation
            setTimeout(() => {
                toast.style.opacity = '1';
                toast.style.transform = 'translateX(0)';
            }, 10);
            
            // Remove toast
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100px)';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        getBorderColor(type) {
            const colors = {
                success: 'rgba(16, 185, 129, 0.5)',
                error: 'rgba(239, 68, 68, 0.5)',
                warning: 'rgba(245, 158, 11, 0.5)',
                info: 'rgba(13, 185, 242, 0.5)'
            };
            return colors[type] || colors.info;
        }
    }

    // ========================================
    // FORM VALIDATION
    // ========================================
    
    class FormValidator {
        static validate(formElement) {
            const inputs = formElement.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('error');
                    isValid = false;
                    
                    // Add shake animation
                    input.style.animation = 'shake 0.3s ease';
                    setTimeout(() => {
                        input.style.animation = '';
                    }, 300);
                } else {
                    input.classList.remove('error');
                }
            });
            
            return isValid;
        }

        static setButtonLoading(button, isLoading) {
            if (isLoading) {
                button.classList.add('loading');
                button.disabled = true;
                button.dataset.originalText = button.textContent;
                button.textContent = 'Loading...';
            } else {
                button.classList.remove('loading');
                button.disabled = false;
                if (button.dataset.originalText) {
                    button.textContent = button.dataset.originalText;
                }
            }
        }
    }

    // ========================================
    // LAZY LOADING IMAGES
    // ========================================
    
    class LazyImageLoader {
        constructor() {
            this.init();
        }

        init() {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.add('loaded');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // ========================================
    // UTILITY FUNCTIONS
    // ========================================
    
    const Utils = {
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        throttle(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                window.VectorSpace.toast.show('Copied to clipboard!', 'success');
            }).catch(() => {
                window.VectorSpace.toast.show('Failed to copy', 'error');
            });
        },

        formatNumber(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        },

        timeAgo(date) {
            const seconds = Math.floor((new Date() - new Date(date)) / 1000);
            
            const intervals = {
                year: 31536000,
                month: 2592000,
                week: 604800,
                day: 86400,
                hour: 3600,
                minute: 60,
                second: 1
            };
            
            for (const [unit, secondsInUnit] of Object.entries(intervals)) {
                const interval = Math.floor(seconds / secondsInUnit);
                if (interval >= 1) {
                    return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
                }
            }
            
            return 'just now';
        }
    };

    // ========================================
    // KEYBOARD SHORTCUTS
    // ========================================
    
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], .topbar-search input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Escape to close modals/dropdowns
            if (e.key === 'Escape') {
                document.querySelectorAll('.user-menu.active').forEach(menu => {
                    menu.classList.remove('active');
                });
                const mobileMenu = document.getElementById('mobileMenu');
                const mobileMenuToggle = document.getElementById('mobileMenuToggle');
                if (mobileMenu && mobileMenu.classList.contains('open')) {
                    mobileMenu.classList.remove('open');
                    mobileMenuToggle.classList.remove('active');
                    document.body.style.overflow = '';
                }
            }
        });
    }

    // ========================================
    // PARALLAX EFFECT FOR PARTICLES
    // ========================================
    
    function initParallax() {
        const particles = document.querySelectorAll('.particle');
        if (particles.length === 0) return;

        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrolled = window.pageYOffset;
                    particles.forEach((particle, index) => {
                        const speed = 0.3 + (index * 0.05);
                        particle.style.transform = `translateY(${scrolled * speed * 0.5}px)`;
                    });
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    // ========================================
    // RIPPLE EFFECT FOR BUTTONS
    // ========================================
    
    function initRippleEffect() {
        document.querySelectorAll('.btn-primary, .btn-secondary, .btn').forEach(button => {
            button.addEventListener('mouseenter', (e) => {
                const rect = button.getBoundingClientRect();
                const ripple = document.createElement('span');
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.3);
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    transform: scale(0);
                    animation: ripple-animation 0.6s linear;
                    pointer-events: none;
                `;
                
                button.style.position = 'relative';
                button.style.overflow = 'hidden';
                button.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    // ========================================
    // INITIALIZE EVERYTHING
    // ========================================
    
    function init() {
        // Initialize controllers
        new HeaderController();
        new MobileMenuController();
        new UserDropdownController();
        new AnimationObserver();
        new LazyImageLoader();
        
        // Initialize features
        initSmoothScroll();
        initKeyboardShortcuts();
        initParallax();
        initRippleEffect();
        
        // Create global toast instance
        window.VectorSpace = window.VectorSpace || {};
        window.VectorSpace.toast = new ToastNotification();
        window.VectorSpace.FormValidator = FormValidator;
        window.VectorSpace.Utils = Utils;
        
        console.log('%c🚀 Vector Space Enhanced UI Loaded', 'color: #0db9f2; font-size: 16px; font-weight: bold;');
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
    `;
    document.head.appendChild(style);

})();
