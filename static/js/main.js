// Main JavaScript for Digital Portfolio

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        }, 5000);
    });

    // Search form enhancement
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="query"]');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function() {
                // Could implement live search suggestions here
                console.log('Search input:', this.value);
            }, 300));
        }
    }

    // Image lazy loading fallback
    const images = document.querySelectorAll('img[data-src]');
    if (images.length > 0 && 'IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Project card hover effects
    const projectCards = document.querySelectorAll('.card');
    projectCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text).then(function() {
                showToast('Link copied to clipboard!', 'success');
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
                fallbackCopyTextToClipboard(text);
            });
        } else {
            fallbackCopyTextToClipboard(text);
        }
    };

    // Fallback copy method
    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        
        // Avoid scrolling to bottom
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showToast('Link copied to clipboard!', 'success');
            } else {
                showToast('Failed to copy link', 'error');
            }
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
            showToast('Failed to copy link', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    // Toast notification system
    window.showToast = function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast show align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove toast element after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    };

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
        return container;
    }

    // Debounce utility function
    function debounce(func, wait, immediate) {
        var timeout;
        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }

    // File input preview functionality
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Find existing preview or create new one
                    let preview = input.parentElement.querySelector('.file-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'file-preview mt-2';
                        input.parentElement.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 150px; object-fit: cover;" alt="Preview">
                        <div class="mt-1 text-muted small">${file.name}</div>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Loading state for forms
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.closest('form').addEventListener('submit', function() {
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
            button.disabled = true;
        });
    });

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

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Initial resize
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    });

    // Search functionality enhancement
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(function(input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                this.blur();
            }
        });
    });

    // Initialize any data tables if present
    if (typeof DataTable !== 'undefined') {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(function(table) {
            new DataTable(table, {
                responsive: true,
                pageLength: 10,
                order: [[0, 'desc']]
            });
        });
    }
});

// Enhanced Like functionality with real-time updates and duplicate prevention
window.toggleLike = function(projectId) {
    const button = event.target.closest('button');
    if (button && button.dataset.processing) {
        return; // Prevent duplicate requests
    }
    
    if (button) {
        button.dataset.processing = 'true';
        button.disabled = true;
    }
    
    fetch(`/api/toggle-like/${projectId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update all like buttons for this project
        const likeButtons = document.querySelectorAll(`[data-project-id="${projectId}"]`);
        likeButtons.forEach(btn => {
            const icon = btn.querySelector('i');
            const countSpan = btn.querySelector('.like-count');
            
            if (data.liked) {
                btn.classList.remove('btn-outline-danger');
                btn.classList.add('btn-danger');
                if (icon) icon.className = 'fas fa-heart';
            } else {
                btn.classList.remove('btn-danger');
                btn.classList.add('btn-outline-danger');
                if (icon) icon.className = 'far fa-heart';
            }
            
            if (countSpan) {
                countSpan.textContent = data.likes_count;
            }
        });
        
        // Update standalone like counts
        const likeCounts = document.querySelectorAll(`.likes-count-${projectId}`);
        likeCounts.forEach(count => {
            count.textContent = data.likes_count;
        });
        
        showToast(data.liked ? 'Projeto curtido!' : 'Curtida removida', 'success');
    })
    .catch(error => {
        console.error('Like error:', error);
        showToast('Erro ao curtir projeto. Tente novamente.', 'error');
    })
    .finally(() => {
        if (button) {
            delete button.dataset.processing;
            button.disabled = false;
        }
    });
};

// Comment functionality with validation and real-time updates
window.submitComment = function(projectId) {
    const form = document.getElementById('comment-form');
    const contentTextarea = form.querySelector('textarea[name="content"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    const content = contentTextarea.value.trim();
    
    // Validation
    if (!content) {
        showToast('O comentário não pode estar vazio.', 'error');
        contentTextarea.focus();
        return;
    }
    
    if (content.length > 1000) {
        showToast('O comentário não pode ter mais de 1000 caracteres.', 'error');
        contentTextarea.focus();
        return;
    }
    
    // Disable form during submission
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
    
    fetch(`/api/add-comment/${projectId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Clear form
        contentTextarea.value = '';
        
        // Add comment to the top of the list
        const commentsList = document.getElementById('comments-list');
        const newCommentHtml = createCommentHtml(data.comment);
        commentsList.insertAdjacentHTML('afterbegin', newCommentHtml);
        
        // Update comment count
        const commentCounts = document.querySelectorAll(`.comments-count-${projectId}`);
        commentCounts.forEach(count => {
            count.textContent = data.total_comments;
        });
        
        showToast('Comentário adicionado com sucesso!', 'success');
    })
    .catch(error => {
        console.error('Comment error:', error);
        showToast('Erro ao adicionar comentário. Tente novamente.', 'error');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Comentar';
    });
};

// Helper function to create comment HTML
function createCommentHtml(comment) {
    const timeAgo = formatTimeAgo(comment.created_at);
    return `
        <div class="comment mb-3 p-3 border rounded">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="d-flex align-items-center">
                    <div class="avatar-placeholder bg-primary text-white rounded-circle me-3 d-flex align-items-center justify-content-center" 
                         style="width: 40px; height: 40px;">
                        <i class="fas fa-user"></i>
                    </div>
                    <div>
                        <h6 class="mb-0 fw-bold">${comment.author_name}</h6>
                        <small class="text-muted">${timeAgo}</small>
                    </div>
                </div>
            </div>
            <p class="mb-0">${comment.content}</p>
        </div>
    `;
}

// Helper function to format time ago
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    
    if (diffDays > 0) {
        return `há ${diffDays} dia${diffDays > 1 ? 's' : ''}`;
    } else if (diffHours > 0) {
        return `há ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
    } else if (diffMinutes > 0) {
        return `há ${diffMinutes} minuto${diffMinutes > 1 ? 's' : ''}`;
    } else {
        return 'agora';
    }
}

// Character count for comment textarea
document.addEventListener('DOMContentLoaded', function() {
    const commentTextareas = document.querySelectorAll('textarea[name="content"]');
    commentTextareas.forEach(textarea => {
        const maxLength = 1000;
        let counter = textarea.parentElement.querySelector('.char-counter');
        
        if (!counter) {
            counter = document.createElement('div');
            counter.className = 'char-counter text-muted small mt-1';
            textarea.parentElement.appendChild(counter);
        }
        
        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${textarea.value.length}/${maxLength} caracteres`;
            counter.className = remaining < 100 ? 'char-counter text-danger small mt-1' : 'char-counter text-muted small mt-1';
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial update
    });
});

// Enhanced form validation
window.validateForm = function(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        if (field.value && !isValidEmail(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // URL validation
    const urlFields = form.querySelectorAll('input[type="url"]');
    urlFields.forEach(function(field) {
        if (field.value && !isValidUrl(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
};

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Page loading indicator
window.addEventListener('beforeunload', function() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    loadingOverlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
    loadingOverlay.style.zIndex = '9999';
    loadingOverlay.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(loadingOverlay);
});
