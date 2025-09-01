// Luxury Real Estate Website - Main JavaScript
// Maeva Investimentos Imobiliários

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // Initialize all components
    initNavigation();
    initHeroSection();
    initPropertySharing();
    initSmoothScrolling();
    initAnimations();
    initFormValidation();
    initImageLazyLoading();
    initTooltips();
    
    console.log('Maeva Investimentos - Website initialized successfully');
});

// Navigation functionality
function initNavigation() {
    const navbar = document.querySelector('.luxury-navbar');
    const navLinks = document.querySelectorAll('.luxury-nav-link');
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.classList.add('active');
        }
    });
    
    // Mobile navigation toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

// Hero section functionality
function initHeroSection() {
    const heroSection = document.querySelector('.hero-section');
    const scrollIndicator = document.querySelector('.hero-scroll-indicator');
    
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', function() {
            const nextSection = heroSection.nextElementSibling;
            if (nextSection) {
                nextSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // Parallax effect for hero background
    window.addEventListener('scroll', function() {
        if (heroSection && window.innerWidth > 768) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        }
    });
}

// Property sharing functionality
function initPropertySharing() {
    const shareButtons = document.querySelectorAll('.share-property');
    const shareModalButton = document.querySelector('.share-modal-property');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const title = this.getAttribute('data-title');
            const url = this.getAttribute('data-url') || window.location.href;
            
            shareProperty(title, url);
        });
    });
    
    if (shareModalButton) {
        shareModalButton.addEventListener('click', function() {
            const modalTitle = document.getElementById('modalTitle').textContent;
            shareProperty(modalTitle, window.location.href);
        });
    }
}

function shareProperty(title, url) {
    const message = `Confira este imóvel exclusivo: ${title}\n\nMaeva Investimentos Imobiliários\n"Conectando pessoas aos melhores imóveis de São Paulo."\n\n${url}`;
    
    // Check if Web Share API is available
    if (navigator.share) {
        navigator.share({
            title: `${title} - Maeva Investimentos`,
            text: message,
            url: url
        }).catch(err => {
            console.log('Error sharing:', err);
            fallbackShare(message);
        });
    } else {
        fallbackShare(message);
    }
}

function fallbackShare(message) {
    // Create share options modal
    const shareOptions = [
        {
            name: 'WhatsApp',
            icon: 'fab fa-whatsapp',
            color: '#25D366',
            action: () => {
                const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
                window.open(whatsappUrl, '_blank');
            }
        },
        {
            name: 'Instagram',
            icon: 'fab fa-instagram',
            color: '#E4405F',
            action: () => {
                // Copy to clipboard for Instagram sharing
                copyToClipboard(message);
                showNotification('Texto copiado! Cole no Instagram para compartilhar.', 'success');
            }
        },
        {
            name: 'LinkedIn',
            icon: 'fab fa-linkedin',
            color: '#0077B5',
            action: () => {
                const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`;
                window.open(linkedinUrl, '_blank');
            }
        },
        {
            name: 'Copiar Link',
            icon: 'fas fa-copy',
            color: '#6c757d',
            action: () => {
                copyToClipboard(message);
                showNotification('Texto copiado para a área de transferência!', 'success');
            }
        }
    ];
    
    showShareModal(shareOptions);
}

function showShareModal(options) {
    // Remove existing modal if present
    const existingModal = document.getElementById('shareModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create share modal
    const modalHTML = `
        <div class="modal fade" id="shareModal" tabindex="-1">
            <div class="modal-dialog modal-sm">
                <div class="modal-content luxury-modal">
                    <div class="modal-header">
                        <h5 class="modal-title luxury-text-gold">Compartilhar</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="share-options">
                            ${options.map(option => `
                                <button class="share-option-btn" data-action="${option.name}" style="--option-color: ${option.color}">
                                    <i class="${option.icon}"></i>
                                    <span>${option.name}</span>
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add event listeners
    const shareModal = document.getElementById('shareModal');
    const shareOptionBtns = shareModal.querySelectorAll('.share-option-btn');
    
    shareOptionBtns.forEach((btn, index) => {
        btn.addEventListener('click', function() {
            options[index].action();
            bootstrap.Modal.getInstance(shareModal).hide();
        });
    });
    
    // Show modal
    const modal = new bootstrap.Modal(shareModal);
    modal.show();
    
    // Clean up when modal is hidden
    shareModal.addEventListener('hidden.bs.modal', function() {
        shareModal.remove();
    });
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                
                const offsetTop = targetElement.offsetTop - 100; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Animation on scroll
function initAnimations() {
    const animateElements = document.querySelectorAll('.luxury-property-card, .service-card, .value-card, .contact-card');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    animateElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// Form validation and enhancement
function initFormValidation() {
    const forms = document.querySelectorAll('.luxury-form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Add floating label effect
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    this.parentElement.classList.remove('focused');
                }
            });
            
            // Real-time validation
            input.addEventListener('input', function() {
                validateInput(this);
            });
        });
    });
    
    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length >= 10) {
                if (value.length === 11) {
                    // Mobile: (11) 98765-4321
                    value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                } else if (value.length === 10) {
                    // Landline: (11) 8765-4321
                    value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
                }
            }
            
            e.target.value = value;
        });
    });
}

function validateInput(input) {
    const value = input.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Remove existing error state
    input.classList.remove('is-invalid');
    const existingError = input.parentElement.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Validation rules
    switch (input.type) {
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (value && !emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Por favor, insira um e-mail válido.';
            }
            break;
            
        case 'tel':
            const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
            if (value && !phoneRegex.test(value)) {
                isValid = false;
                errorMessage = 'Por favor, insira um telefone válido.';
            }
            break;
    }
    
    // Required field validation
    if (input.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo é obrigatório.';
    }
    
    // Show error state
    if (!isValid) {
        input.classList.add('is-invalid');
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        errorElement.textContent = errorMessage;
        input.parentElement.appendChild(errorElement);
    }
    
    return isValid;
}

// Lazy loading for images
function initImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Tooltips initialization
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Utility functions
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
        
        textArea.remove();
    }
}

function showNotification(message, type = 'info') {
    // Remove existing notification
    const existingNotification = document.querySelector('.luxury-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `luxury-notification luxury-notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--luxury-dark);
        color: var(--luxury-white);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--luxury-gold);
        z-index: 9999;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        animation: slideInRight 0.3s ease;
        max-width: 350px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    `;
    
    document.body.appendChild(notification);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', function() {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Property card hover effects
document.addEventListener('DOMContentLoaded', function() {
    const propertyCards = document.querySelectorAll('.luxury-property-card');
    
    propertyCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Back to top button
window.addEventListener('scroll', function() {
    const scrollButton = getOrCreateBackToTopButton();
    
    if (window.pageYOffset > 300) {
        scrollButton.style.display = 'block';
        setTimeout(() => scrollButton.style.opacity = '1', 10);
    } else {
        scrollButton.style.opacity = '0';
        setTimeout(() => scrollButton.style.display = 'none', 300);
    }
});

function getOrCreateBackToTopButton() {
    let scrollButton = document.getElementById('backToTop');
    
    if (!scrollButton) {
        scrollButton = document.createElement('button');
        scrollButton.id = 'backToTop';
        scrollButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
        scrollButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: var(--luxury-gold);
            color: var(--luxury-black);
            border: none;
            border-radius: 50%;
            font-size: 1.2rem;
            cursor: pointer;
            z-index: 1000;
            display: none;
            opacity: 0;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
        `;
        
        scrollButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        scrollButton.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.boxShadow = '0 8px 25px rgba(212, 175, 55, 0.4)';
        });
        
        scrollButton.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 5px 15px rgba(212, 175, 55, 0.3)';
        });
        
        document.body.appendChild(scrollButton);
    }
    
    return scrollButton;
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .share-options {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    .share-option-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: var(--luxury-white);
        padding: 1rem;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .share-option-btn:hover {
        background: var(--option-color);
        border-color: var(--option-color);
        color: white;
        transform: translateY(-2px);
    }
    
    .share-option-btn i {
        font-size: 1.5rem;
    }
    
    .share-option-btn span {
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: var(--luxury-white);
        cursor: pointer;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        transition: all 0.2s ease;
    }
    
    .notification-close:hover {
        color: var(--luxury-gold);
    }
    
    .luxury-navbar.scrolled {
        background: rgba(10, 10, 10, 0.98) !important;
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
    }
    
    .form-control.is-invalid {
        border-color: #dc3545;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
    }
    
    .invalid-feedback {
        width: 100%;
        margin-top: 0.25rem;
        font-size: 0.875rem;
        color: #dc3545;
    }
`;

document.head.appendChild(style);

// Performance optimization
window.addEventListener('load', function() {
    // Mark page as fully loaded
    document.body.classList.add('page-loaded');
    
    // Initialize any remaining components that need full page load
    console.log('Maeva Investimentos - All resources loaded');
});

// Advanced Filters Functionality
function toggleAdvancedFilters() {
    const advancedFilters = document.getElementById('advancedFilters');
    const toggle = document.querySelector('.advanced-filters-toggle button');
    
    if (advancedFilters.style.display === 'none') {
        advancedFilters.style.display = 'block';
        toggle.innerHTML = '<i class="fas fa-cog me-2"></i>Ocultar Filtros Avançados';
    } else {
        advancedFilters.style.display = 'none';
        toggle.innerHTML = '<i class="fas fa-cog me-2"></i>Filtros Avançados';
    }
}

// Apply Filters Function
function applyFilters() {
    const typeFilter = document.getElementById('typeFilter')?.value || '';
    const locationFilter = document.getElementById('locationFilter')?.value || '';
    const priceFilter = document.getElementById('priceFilter')?.value || '';
    const bedroomsFilter = document.getElementById('bedroomsFilter')?.value || '';
    const bathroomsFilter = document.getElementById('bathroomsFilter')?.value || '';
    const areaFilter = document.getElementById('areaFilter')?.value || '';
    
    // Get selected amenities
    const amenities = [];
    document.querySelectorAll('.amenities-checkboxes input[type="checkbox"]:checked').forEach(checkbox => {
        amenities.push(checkbox.value);
    });
    
    // Get all property cards
    const propertyCards = document.querySelectorAll('.luxury-property-card');
    let visibleCount = 0;
    
    propertyCards.forEach(card => {
        const cardContainer = card.closest('.col-lg-4, .col-md-6');
        let shouldShow = true;
        
        // Get property data from card
        const cardType = card.querySelector('.property-type-badge')?.textContent.toLowerCase() || '';
        const cardLocation = card.querySelector('.property-location')?.textContent.toLowerCase() || '';
        const cardPrice = card.querySelector('.property-price')?.textContent || '';
        
        // Filter by type
        if (typeFilter && !cardType.includes(typeFilter)) {
            shouldShow = false;
        }
        
        // Filter by location
        if (locationFilter && !cardLocation.includes(locationFilter)) {
            shouldShow = false;
        }
        
        // Filter by price (basic implementation)
        if (priceFilter && cardPrice) {
            // This is a simplified price filter - in a real implementation you'd parse the price properly
            shouldShow = shouldShow && cardPrice !== '';
        }
        
        // Show/hide card
        if (shouldShow) {
            cardContainer.style.display = 'block';
            visibleCount++;
        } else {
            cardContainer.style.display = 'none';
        }
    });
    
    // Update results count
    updateResultsCount(visibleCount);
}

// Update results count
function updateResultsCount(count) {
    let resultsCounter = document.querySelector('.results-counter');
    if (!resultsCounter) {
        // Create results counter if it doesn't exist
        resultsCounter = document.createElement('div');
        resultsCounter.className = 'results-counter text-center mb-4';
        const gallerySection = document.querySelector('.py-5 .container');
        if (gallerySection) {
            gallerySection.insertBefore(resultsCounter, gallerySection.firstChild);
        }
    }
    
    resultsCounter.innerHTML = `
        <p class="text-white-50">
            <i class="fas fa-home me-2 luxury-text-gold"></i>
            ${count} ${count === 1 ? 'imóvel encontrado' : 'imóveis encontrados'}
        </p>
    `;
}

// Clear all filters
function clearFilters() {
    document.getElementById('typeFilter').value = '';
    document.getElementById('locationFilter').value = '';
    document.getElementById('priceFilter').value = '';
    document.getElementById('bedroomsFilter').value = '';
    document.getElementById('bathroomsFilter').value = '';
    document.getElementById('areaFilter').value = '';
    
    // Clear checkboxes
    document.querySelectorAll('.amenities-checkboxes input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Show all properties
    document.querySelectorAll('.luxury-property-card').forEach(card => {
        card.closest('.col-lg-4, .col-md-6').style.display = 'block';
    });
    
    // Update count
    const totalCount = document.querySelectorAll('.luxury-property-card').length;
    updateResultsCount(totalCount);
}
