/**
 * Modern Digital Portfolio - JavaScript
 * Enhanced UI/UX with animations and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializePortfolio();
});

function initializePortfolio() {
    initTheme();
    initAnimations();
    initFormEnhancements();
    initTooltips();
    initImageUploads();
    initAlerts();
    initSmoothScrolling();
}

// Theme Management
function initTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);

    // Add smooth transition
    document.body.style.transition = 'all 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Animation System
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animations
    document.querySelectorAll('.card, .hero-content, .project-card').forEach(el => {
        observer.observe(el);
    });

    // Add stagger animation to project cards
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('slide-up');
    });
}

// Enhanced Form Functionality
function initFormEnhancements() {
    // Add loading animation to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                showLoadingState(submitBtn);

                // Reset after timeout as fallback
                setTimeout(() => {
                    hideLoadingState(submitBtn);
                }, 10000);
            }
        });
    });

    // Enhanced form validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearValidation);
    });

    // Admin action confirmations
    document.querySelectorAll('.admin-action').forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.dataset.action;
            const target = this.dataset.target;

            if (!confirm(`Are you sure you want to ${action} ${target}?`)) {
                e.preventDefault();
            }
        });
    });
}

function showLoadingState(button) {
    const originalContent = button.innerHTML;
    button.dataset.originalContent = originalContent;
    button.innerHTML = '<span class="loading me-2"></span>Processing...';
    button.disabled = true;
    button.classList.add('loading-state');
}

function hideLoadingState(button) {
    if (button.dataset.originalContent) {
        button.innerHTML = button.dataset.originalContent;
        delete button.dataset.originalContent;
    }
    button.disabled = false;
    button.classList.remove('loading-state');
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();

    // Clear previous validation
    field.classList.remove('is-valid', 'is-invalid');

    if (field.required && !value) {
        field.classList.add('is-invalid');
        showFieldError(field, 'This field is required.');
    } else if (field.type === 'email' && value && !isValidEmail(value)) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Please enter a valid email address.');
    } else if (value) {
        field.classList.add('is-valid');
        clearFieldError(field);
    }
}

function clearValidation(e) {
    const field = e.target;
    field.classList.remove('is-valid', 'is-invalid');
    clearFieldError(field);
}

function showFieldError(field, message) {
    clearFieldError(field);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Tooltip Enhancement
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Image Upload Preview
function initImageUploads() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');

    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) { // 5MB limit
                    alert('File size must be less than 5MB');
                    this.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = findImagePreview(input);
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.transform = 'scale(1.05)';
                        setTimeout(() => {
                            preview.style.transform = '';
                        }, 200);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

function findImagePreview(input) {
    // Look for various preview patterns
    const previewSelectors = [
        '.profile-image',
        '.image-preview',
        'img[data-preview]',
        '.preview-image'
    ];

    for (const selector of previewSelectors) {
        const preview = input.closest('.form-group, .mb-3, .profile-upload')?.querySelector(selector);
        if (preview) return preview;
    }

    return null;
}

// Alert Management
function initAlerts() {
    // Auto-hide alerts with smooth animation
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';

            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 500);
        });
    }, 5000);
}

// Smooth Scrolling
function initSmoothScrolling() {
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href !== '#' && href.length > 1) {
                try {
                    // Validate selector before using querySelector
                    if (href.match(/^#[\w-]+$/)) {
                        const target = document.querySelector(href);
                        if (target) {
                            e.preventDefault();
                            target.scrollIntoView({
                                behavior: 'smooth',
                                block: 'start'
                            });
                        }
                    }
                } catch (err) {
                    console.log('Invalid selector:', href);
                }
            } else if (href === '#') {
                // Prevent default action for empty hash links
                e.preventDefault();
            }
        });
    });
}

// Project Card Interactions
function initProjectCards() {
    const projectCards = document.querySelectorAll('.project-card');

    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

// Like System with Animation
function toggleLike(projectId) {
    if (!projectId || projectId === '') return;

    const button = document.querySelector(`[data-project-id="${projectId}"]`);
    if (!button) return;

    const icon = button.querySelector('i');
    const countSpan = button.querySelector('.like-count');

    // Add loading state
    icon.classList.add('fa-spin');

    fetch(`/toggle_like/${projectId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading state
        icon.classList.remove('fa-spin');

        // Update UI
        if (data.liked) {
            icon.classList.remove('far');
            icon.classList.add('fas', 'text-danger');
            button.classList.add('liked');

            // Heart animation
            icon.style.transform = 'scale(1.3)';
            setTimeout(() => {
                icon.style.transform = '';
            }, 200);
        } else {
            icon.classList.remove('fas', 'text-danger');
            icon.classList.add('far');
            button.classList.remove('liked');
        }

        // Update count with animation
        if (countSpan) {
            countSpan.style.transform = 'scale(1.2)';
            countSpan.textContent = data.likes_count;
            setTimeout(() => {
                countSpan.style.transform = '';
            }, 200);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        icon.classList.remove('fa-spin');
        alert('An error occurred. Please try again.');
    });
}

// Search Enhancement
function initSearch() {
    const searchInput = document.querySelector('input[name="query"]');
    const searchForm = searchInput?.closest('form');

    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);

            if (this.value.length >= 3) {
                searchTimeout = setTimeout(() => {
                    // Could implement live search here
                    console.log('Searching for:', this.value);
                }, 300);
            }
        });

        // Add search suggestions (placeholder for future enhancement)
        searchInput.addEventListener('focus', function() {
            this.classList.add('search-focused');
        });

        searchInput.addEventListener('blur', function() {
            this.classList.remove('search-focused');
        });
    }
}

// Admin Panel Enhancements
function initAdminPanel() {
    // Row highlighting in admin tables
    const adminRows = document.querySelectorAll('.admin-table tbody tr');
    adminRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'var(--bg-tertiary)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Bulk actions (future enhancement)
    const checkboxes = document.querySelectorAll('.admin-checkbox');
    if (checkboxes.length > 0) {
        const selectAllCheckbox = document.querySelector('#select-all');

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                checkboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
        }
    }
}

// Utility Functions
function debounce(func, wait) {
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

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    initProjectCards();
    initAdminPanel();
});

// Performance monitoring (development only)
if (window.location.hostname === 'localhost' || window.location.hostname.includes('replit')) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page Load Time:', Math.round(perfData.loadEventEnd - perfData.loadEventStart), 'ms');
        }, 100);
    });
}