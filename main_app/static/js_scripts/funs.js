// ==================== Global Utilities ====================

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Only prevent default if it's not just '#'
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const navHeight = document.querySelector('.welcome-nav')?.offsetHeight || 0;
                    const targetPosition = targetElement.offsetTop - navHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});

// Add scroll-based navbar shadow
window.addEventListener('scroll', function() {
    const nav = document.querySelector('.welcome-nav');
    if (nav) {
        if (window.scrollY > 50) {
            nav.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
        } else {
            nav.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        }
    }
});

// ==================== Form Handling (For Future Pages) ====================

// Generic CSRF token getter
function getCSRFToken() {
    const tokenInput = document.querySelector('input[name="csrf_token"]');
    return tokenInput ? tokenInput.value : null;
}

// Generic form submission handler with CSRF protection
function handleFormSubmit(formElement, successCallback, errorCallback) {
    formElement.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(formElement);
        const csrfToken = getCSRFToken();
        
        if (!csrfToken) {
            console.error('CSRF token not found');
            if (errorCallback) errorCallback('Security token missing. Please refresh the page.');
            return;
        }
        
        try {
            const response = await fetch(formElement.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            
            const data = await response.json();
            
            if (response.ok && successCallback) {
                successCallback(data);
            } else if (errorCallback) {
                errorCallback(data.message || 'An error occurred');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            if (errorCallback) errorCallback('Network error. Please try again.');
        }
    });
}

// ==================== Animation Utilities ====================

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply fade-in animation to elements
document.addEventListener('DOMContentLoaded', function() {
    const animatedElements = document.querySelectorAll('.welcome-feature-card, .welcome-reason-item, .welcome-timeline-item');
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// ==================== Welcome Page Specific ====================

// Add parallax effect to hero section
window.addEventListener('scroll', function() {
    const heroVisual = document.querySelector('.welcome-hero-visual');
    if (heroVisual) {
        const scrolled = window.pageYOffset;
        heroVisual.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});


// ==================== Password Toggle Functionality ====================
function togglePassword(fieldName) {
    const input = document.querySelector(`input[name="${fieldName}"]`);
    
    if (!input) {
        console.error(`Input field with name "${fieldName}" not found`);
        return;
    }
    
    const wrapper = input.parentElement;
    const button = wrapper.querySelector('.signup-password-toggle, .signin-password-toggle, .reset-password-toggle, .change-password-toggle, .admin-password-toggle, .adminsign-password-toggle');
    const icon = button ? button.querySelector('.signup-eye-icon, .signin-eye-icon, .reset-eye-icon, .change-eye-icon, .admin-eye-icon, .adminsign-eye-icon') : null;
    
    if (!icon) {
        console.error('Eye icon not found');
        return;
    }
    
    if (input.type === 'password') {
        input.type = 'text';
        // Change to eye-off icon
        icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
    } else {
        input.type = 'password';
        // Change back to eye icon
        icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
    }
}




// ==================== Password Strength Checker ====================
document.addEventListener('DOMContentLoaded', function() {
    // For reset password page
    const newPasswordInput = document.querySelector('input[name="new_password"]');
    
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }
    
    // For change password page (different IDs)
    const changeNewPasswordInput = document.querySelector('input[name="new_password"]');
    
    if (changeNewPasswordInput && document.getElementById('changePasswordStrength')) {
        changeNewPasswordInput.addEventListener('input', function() {
            checkChangePasswordStrength(this.value);
        });
    }
});

function checkPasswordStrength(password) {
    const strengthBar = document.getElementById('passwordStrength');
    const strengthText = document.getElementById('strengthText');
    
    if (!strengthBar || !strengthText) return;
    
    if (password.length === 0) {
        strengthBar.className = 'reset-strength-fill';
        strengthText.className = 'reset-strength-text';
        strengthText.textContent = 'Password strength';
        return;
    }
    
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    
    // Contains lowercase
    if (/[a-z]/.test(password)) strength++;
    
    // Contains uppercase
    if (/[A-Z]/.test(password)) strength++;
    
    // Contains number
    if (/[0-9]/.test(password)) strength++;
    
    // Contains special character
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    // Determine strength level
    if (strength <= 2) {
        strengthBar.className = 'reset-strength-fill weak';
        strengthText.className = 'reset-strength-text weak';
        strengthText.textContent = 'Weak password';
    } else if (strength <= 4) {
        strengthBar.className = 'reset-strength-fill medium';
        strengthText.className = 'reset-strength-text medium';
        strengthText.textContent = 'Medium password';
    } else {
        strengthBar.className = 'reset-strength-fill strong';
        strengthText.className = 'reset-strength-text strong';
        strengthText.textContent = 'Strong password';
    }
}

function checkChangePasswordStrength(password) {
    const strengthBar = document.getElementById('changePasswordStrength');
    const strengthText = document.getElementById('changeStrengthText');
    
    if (!strengthBar || !strengthText) return;
    
    if (password.length === 0) {
        strengthBar.className = 'change-strength-fill';
        strengthText.className = 'change-strength-text';
        strengthText.textContent = 'Password strength';
        return;
    }
    
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    
    // Contains lowercase
    if (/[a-z]/.test(password)) strength++;
    
    // Contains uppercase
    if (/[A-Z]/.test(password)) strength++;
    
    // Contains number
    if (/[0-9]/.test(password)) strength++;
    
    // Contains special character
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    // Determine strength level
    if (strength <= 2) {
        strengthBar.className = 'change-strength-fill weak';
        strengthText.className = 'change-strength-text weak';
        strengthText.textContent = 'Weak password';
    } else if (strength <= 4) {
        strengthBar.className = 'change-strength-fill medium';
        strengthText.className = 'change-strength-text medium';
        strengthText.textContent = 'Medium password';
    } else {
        strengthBar.className = 'change-strength-fill strong';
        strengthText.className = 'change-strength-text strong';
        strengthText.textContent = 'Strong password';
    }
}


// ==================== Create Section Live Preview ====================
document.addEventListener('DOMContentLoaded', function() {
    const sectionInput = document.querySelector('input[name="section"]');
    const sectionCodeInput = document.querySelector('input[name="section_code"]');
    
    if (sectionInput) {
        sectionInput.addEventListener('input', updateSectionPreview);
    }
    
    if (sectionCodeInput) {
        sectionCodeInput.addEventListener('input', updateSectionPreview);
    }
});

function updateSectionPreview() {
    const sectionInput = document.querySelector('input[name="section"]');
    const sectionCodeInput = document.querySelector('input[name="section_code"]');
    const previewSection = document.getElementById('previewSection');
    const previewCode = document.getElementById('previewCode');
    const previewCodeSection = document.getElementById('previewCodeSection');
    
    if (!previewSection) return;
    
    // Update section name preview
    if (sectionInput && sectionInput.value.trim() !== '') {
        previewSection.textContent = sectionInput.value;
    } else {
        previewSection.textContent = 'Your Section Name';
    }
    
    // Update section code preview
    if (sectionCodeInput && sectionCodeInput.value.trim() !== '') {
        previewCode.textContent = sectionCodeInput.value;
        previewCodeSection.style.display = 'block';
    } else {
        previewCodeSection.style.display = 'none';
    }
}



// ==================== File Upload Handler ====================
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
        
        // Drag and drop functionality
        const fileLabel = fileInput.nextElementSibling;
        
        fileLabel.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#667eea';
            this.style.background = 'rgba(102, 126, 234, 0.1)';
        });
        
        fileLabel.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderColor = '#e0e0e0';
            this.style.background = '#f8f9fa';
        });
        
        fileLabel.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#e0e0e0';
            this.style.background = '#f8f9fa';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect({ target: fileInput });
            }
        });
    }
});

function handleFileSelect(event) {
    const file = event.target.files[0];
    const fileSelected = document.getElementById('fileSelected');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileLabel = event.target.nextElementSibling;
    
    if (file) {
        // Show selected file info
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileSelected.style.display = 'flex';
        fileLabel.style.display = 'none';
    }
}

function removeFile() {
    const fileInput = document.getElementById('fileInput');
    const fileSelected = document.getElementById('fileSelected');
    const fileLabel = document.querySelector('.upload-file-label');
    
    if (fileInput) {
        fileInput.value = '';
        fileSelected.style.display = 'none';
        fileLabel.style.display = 'flex';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}



// Initialize file size display
document.addEventListener('DOMContentLoaded', function() {
    const fileSizes = document.querySelectorAll('.view-file-size');
    fileSizes.forEach(function(element) {
        const bytes = parseInt(element.getAttribute('data-size'));
        element.textContent = formatFileSize(bytes);
    });
});


function confirmDelete(fileId, fileName) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const fileNameElement = document.getElementById('deleteFileName');
    
    // Set the file name
    fileNameElement.textContent = fileName;
    
    // Set the form action
    form.action = `/delete-file/${fileId}`;
    //form.action = "{{ url_for('main_bp.delete_file', file_id='FILE_ID') }}".replace('FILE_ID', fileId);
    
    // Show modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal on ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeDeleteModal();
    }
});

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}



// Copy link to clipboard
function copyLink(sectionId) {
    const linkInput = document.getElementById('link-' + sectionId);
    linkInput.select();
    linkInput.setSelectionRange(0, 99999); // For mobile devices
    
    navigator.clipboard.writeText(linkInput.value).then(function() {
        showToast();
    }).catch(function(err) {
        // Fallback for older browsers
        document.execCommand('copy');
        showToast();
    });
}

function showToast() {
    const toast = document.getElementById('copyToast');
    toast.classList.add('dashboard-toast-show');
    
    setTimeout(function() {
        toast.classList.remove('dashboard-toast-show');
    }, 3000);
}

// Delete All Files Modal
function confirmDeleteAll(sectionId, sectionName) {
    const modal = document.getElementById('deleteAllModal');
    const form = document.getElementById('deleteAllForm');
    const nameElement = document.getElementById('deleteAllSectionName');
    
    nameElement.textContent = sectionName;
    form.action = `/delete-files/${sectionId}`;
    //form.action = "{{ url_for('delete_all_files', section_id='SECTION_ID') }}".replace('SECTION_ID', sectionId);
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeDeleteAllModal() {
    const modal = document.getElementById('deleteAllModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Delete Section Link Modal
function confirmDeleteLink(sectionId, sectionName) {
    const modal = document.getElementById('deleteLinkModal');
    const form = document.getElementById('deleteLinkForm');
    const nameElement = document.getElementById('deleteLinkSectionName');
    
    nameElement.textContent = sectionName;
    form.action = `/delete-section/${sectionId}`;
    //form.action = "{{ url_for('delete_section', section_id='SECTION_ID') }}".replace('SECTION_ID', sectionId);
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeDeleteLinkModal() {
    const modal = document.getElementById('deleteLinkModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modals on ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeDeleteAllModal();
        closeDeleteLinkModal();
    }
});


// Admin Base HTML

function toggleSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    const main = document.getElementById('adminMain');
    const overlay = document.getElementById('sidebarOverlay');
    
    sidebar.classList.toggle('collapsed');
    main.classList.toggle('expanded');
    
    // For mobile
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle('mobile-open');
        overlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : 'auto';
    }
}

// Close sidebar on mobile when clicking a link
document.querySelectorAll('.admin-nav-link').forEach(link => {
    link.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
            toggleSidebar();
        }
    });
});




// ==================== User Detail Page JavaScript ====================

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeUserDetailPage();
});

function initializeUserDetailPage() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize section card interactions
    initializeSectionCards();
    
    // Initialize activity timeline animations
    initializeTimelineAnimations();
    
    // Add copy functionality for section codes
    initializeSectionCodeCopy();
}

// Initialize tooltips for various elements
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const text = event.currentTarget.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'user-detail-tooltip';
    tooltip.textContent = text;
    tooltip.style.position = 'absolute';
    tooltip.style.background = 'rgba(0, 0, 0, 0.8)';
    tooltip.style.color = 'white';
    tooltip.style.padding = '0.5rem 0.75rem';
    tooltip.style.borderRadius = '6px';
    tooltip.style.fontSize = '0.85rem';
    tooltip.style.zIndex = '1000';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.whiteSpace = 'nowrap';
    
    document.body.appendChild(tooltip);
    
    const rect = event.currentTarget.getBoundingClientRect();
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
    tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
    
    event.currentTarget._tooltip = tooltip;
}

function hideTooltip(event) {
    if (event.currentTarget._tooltip) {
        event.currentTarget._tooltip.remove();
        delete event.currentTarget._tooltip;
    }
}

// Initialize section card interactions
function initializeSectionCards() {
    const sectionCards = document.querySelectorAll('.user-detail-section-card');
    
    sectionCards.forEach(card => {
        // Add ripple effect on click
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.user-detail-section-action')) {
                createRipple(e, this);
            }
        });
    });
}

function createRipple(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(76, 175, 80, 0.3)';
    ripple.style.transform = 'scale(0)';
    ripple.style.animation = 'ripple-animation 0.6s ease-out';
    ripple.style.pointerEvents = 'none';
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// Add ripple animation styles
if (!document.getElementById('ripple-animation-style')) {
    const style = document.createElement('style');
    style.id = 'ripple-animation-style';
    style.textContent = `
        @keyframes ripple-animation {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize timeline animations
function initializeTimelineAnimations() {
    const timelineItems = document.querySelectorAll('.user-detail-timeline-item');
    
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateX(0)';
            }
        });
    }, observerOptions);
    
    timelineItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(item);
    });
}

// Copy section code to clipboard
function initializeSectionCodeCopy() {
    const sectionCodes = document.querySelectorAll('.user-detail-section-code');
    
    sectionCodes.forEach(codeElement => {
        codeElement.style.cursor = 'pointer';
        codeElement.setAttribute('title', 'Click to copy section code');
        
        codeElement.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const code = this.textContent.trim();
            copySectionCode(code, this);
        });
    });
}

function copySectionCode(code, element) {
    navigator.clipboard.writeText(code).then(function() {
        showCopyFeedback(element, 'Copied!');
    }).catch(function() {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = code;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showCopyFeedback(element, 'Copied!');
    });
}

function showCopyFeedback(element, message) {
    const originalText = element.textContent;
    element.textContent = message;
    element.style.background = '#e8f5e9';
    
    setTimeout(() => {
        element.textContent = originalText;
        element.style.background = '';
    }, 1500);
}

// Format dates to relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

// Update all timestamps on page
function updateTimestamps() {
    const timestamps = document.querySelectorAll('[data-timestamp]');
    
    timestamps.forEach(timestamp => {
        const dateString = timestamp.getAttribute('data-timestamp');
        timestamp.textContent = formatRelativeTime(dateString);
    });
}

// Call updateTimestamps on page load and periodically
document.addEventListener('DOMContentLoaded', function() {
    updateTimestamps();
    // Update timestamps every minute
    setInterval(updateTimestamps, 60000);
});

// Smooth scroll to sections
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const navHeight = document.querySelector('.user-detail-topnav')?.offsetHeight || 0;
        const targetPosition = section.offsetTop - navHeight - 20;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

// Filter sections (if search/filter functionality is added)
function filterSections(searchTerm) {
    const sectionCards = document.querySelectorAll('.user-detail-section-card');
    const searchLower = searchTerm.toLowerCase();
    let visibleCount = 0;
    
    sectionCards.forEach(card => {
        const sectionName = card.querySelector('.user-detail-section-name')?.textContent.toLowerCase() || '';
        const sectionCode = card.querySelector('.user-detail-section-code')?.textContent.toLowerCase() || '';
        
        if (sectionName.includes(searchLower) || sectionCode.includes(searchLower)) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide empty state
    const emptyState = document.querySelector('.user-detail-empty-state');
    if (emptyState) {
        emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }
    
    return visibleCount;
}

// Export user data (if needed)
function exportUserData(userId) {
    // This would trigger a download of user data in JSON or CSV format
    console.log('Exporting data for user:', userId);
    
    // Create a simple export notification
    showNotification('Preparing user data export...', 'info');
    
    // In a real implementation, this would make an API call to get the export
    // For now, just show a success message
    setTimeout(() => {
        showNotification('User data exported successfully!', 'success');
    }, 2000);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `user-detail-notification user-detail-notification-${type}`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '1rem 1.5rem';
    notification.style.background = type === 'success' ? '#e8f5e9' : '#e3f2fd';
    notification.style.color = type === 'success' ? '#2e7d32' : '#1976d2';
    notification.style.borderRadius = '10px';
    notification.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.15)';
    notification.style.zIndex = '10000';
    notification.style.animation = 'slideInRight 0.3s ease-out';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles for notifications
if (!document.getElementById('notification-animation-style')) {
    const style = document.createElement('style');
    style.id = 'notification-animation-style';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
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
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Refresh user statistics
function refreshUserStats(userId) {
    showNotification('Refreshing user statistics...', 'info');
    
    // In a real implementation, this would make an API call
    // For now, just reload the page
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

// Navigate to section detail
function navigateToSection(sectionId) {
    // Construct the URL for the section detail page
    window.location.href = `/admin/section/${sectionId}`;
}



// Admin User Creation Part
// ==================== Create User Page JavaScript ====================

document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    const form = document.getElementById('createUserForm');

    // Password strength checker
    if (password1Input) {
        password1Input.addEventListener('input', function() {
            checkPasswordStrength1(this.value);
        });
    }

    // Password match checker
    if (password2Input) {
        password2Input.addEventListener('input', checkPasswordMatch);
    }

    if (password1Input) {
        password1Input.addEventListener('input', checkPasswordMatch);
    }

    // Form validation before submit
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });
    }

    // Real-time validation for inputs
    const inputs = document.querySelectorAll('.createuser-input');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
});

/**
 * Check password strength and update indicator
 */
function checkPasswordStrength1(password) {
    const strengthBar = document.getElementById('passwordStrengths');
    const strengthText = document.getElementById('strengthTexts');
    
    if (!strengthBar || !strengthText) return;
    
    if (password.length === 0) {
        strengthBar.className = 'createuser-strength-fill';
        strengthText.className = 'createuser-strength-text';
        strengthText.textContent = 'Password strength';
        return;
    }
    
    let strength = 0;
    
    // Length checks
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    
    // Contains lowercase
    if (/[a-z]/.test(password)) strength++;
    
    // Contains uppercase
    if (/[A-Z]/.test(password)) strength++;
    
    // Contains number
    if (/[0-9]/.test(password)) strength++;
    
    // Contains special character
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    // Determine strength level
    if (strength <= 2) {
        strengthBar.className = 'createuser-strength-fill weak';
        strengthText.className = 'createuser-strength-text weak';
        strengthText.textContent = 'Weak password';
    } else if (strength <= 4) {
        strengthBar.className = 'createuser-strength-fill medium';
        strengthText.className = 'createuser-strength-text medium';
        strengthText.textContent = 'Medium password';
    } else {
        strengthBar.className = 'createuser-strength-fill strong';
        strengthText.className = 'createuser-strength-text strong';
        strengthText.textContent = 'Strong password';
    }
}

/**
 * Check if passwords match
 */
function checkPasswordMatch() {
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');
    const matchIndicator = document.getElementById('passwordMatch');
    
    if (!password1 || !password2 || !matchIndicator) return;
    
    const pass1Value = password1.value;
    const pass2Value = password2.value;
    
    if (pass2Value.length === 0) {
        matchIndicator.style.display = 'none';
        return;
    }
    
    if (pass1Value === pass2Value && pass2Value.length > 0) {
        matchIndicator.style.display = 'flex';
        matchIndicator.className = 'createuser-match-indicator';
        matchIndicator.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>Passwords match</span>
        `;
    } else {
        matchIndicator.style.display = 'flex';
        matchIndicator.className = 'createuser-match-indicator no-match';
        matchIndicator.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            <span>Passwords do not match</span>
        `;
    }
}

/**
 * Toggle password visibility
 */
function togglePassword1(fieldId) {
    const input = document.getElementById(fieldId);
    
    if (!input) {
        console.error(`Input field with id "${fieldId}" not found`);
        return;
    }
    
    const wrapper = input.closest('.createuser-password-wrapper');
    const button = wrapper.querySelector('.createuser-password-toggle');
    const icon = button.querySelector('.createuser-eye-icon');
    
    if (!icon) {
        console.error('Eye icon not found');
        return;
    }
    
    if (input.type === 'password') {
        input.type = 'text';
        // Change to eye-off icon
        icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
    } else {
        input.type = 'password';
        // Change back to eye icon
        icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
    }
}

/**
 * Validate individual field
 */
function validateField(field) {
    const fieldName = field.name;
    const fieldValue = field.value.trim();
    
    // Remove any existing error messages
    const existingError = field.parentElement.querySelector('.createuser-field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Reset field styling
    field.style.borderColor = '#e0e0e0';
    
    let isValid = true;
    let errorMessage = '';
    
    switch(fieldName) {
        case 'username':
            if (fieldValue.length === 0) {
                isValid = false;
                errorMessage = 'Username is required';
            } else if (fieldValue.length < 3) {
                isValid = false;
                errorMessage = 'Username must be at least 3 characters';
            } else if (!/^[a-zA-Z0-9_ ]+$/.test(fieldValue)) {
                isValid = false;
                errorMessage = 'Username can only contain letters, numbers, and underscores';
            }
            break;
            
        case 'email':
            if (fieldValue.length === 0) {
                isValid = false;
                errorMessage = 'Email is required';
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fieldValue)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
            break;
            
        case 'password1':
            if (fieldValue.length === 0) {
                isValid = false;
                errorMessage = 'Password is required';
            } else if (fieldValue.length < 8) {
                isValid = false;
                errorMessage = 'Password must be at least 8 characters';
            }
            break;
            
        case 'password2':
            const password1 = document.getElementById('password1');
            if (fieldValue.length === 0) {
                isValid = false;
                errorMessage = 'Please confirm your password';
            } else if (password1 && fieldValue !== password1.value) {
                isValid = false;
                errorMessage = 'Passwords do not match';
            }
            break;
    }
    
    if (!isValid) {
        field.style.borderColor = '#ff4444';
        const errorDiv = document.createElement('div');
        errorDiv.className = 'createuser-field-error';
        errorDiv.style.color = '#ff4444';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        errorDiv.innerHTML = `⚠ ${errorMessage}`;
        field.parentElement.appendChild(errorDiv);
    }
    
    return isValid;
}

/**
 * Validate entire form before submission
 */
function validateForm() {
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');
    
    let isValid = true;
    
    // Validate all fields
    if (username && !validateField(username)) isValid = false;
    if (email && !validateField(email)) isValid = false;
    if (password1 && !validateField(password1)) isValid = false;
    if (password2 && !validateField(password2)) isValid = false;
    
    // Check password strength
    if (password1 && password1.value.length > 0) {
        const strengthBar = document.getElementById('passwordStrength');
        if (strengthBar && strengthBar.classList.contains('weak')) {
            // Show warning but don't prevent submission
            console.warn('Weak password detected');
        }
    }
    
    // Scroll to first error if validation fails
    if (!isValid) {
        const firstError = document.querySelector('.createuser-field-error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    return isValid;
}

/**
 * Auto-focus first empty field on page load
 */
window.addEventListener('load', function() {
    const username = document.getElementById('username');
    if (username && username.value.trim() === '') {
        username.focus();
    }
});

/**
 * Prevent form re-submission on page refresh
 */
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

/**
 * Show confirmation before leaving page with unsaved changes
 */
let formModified = false;

document.querySelectorAll('.createuser-input').forEach(input => {
    input.addEventListener('change', function() {
        formModified = true;
    });
});

window.addEventListener('beforeunload', function(e) {
    if (formModified) {
        e.preventDefault();
        e.returnValue = '';
        return '';
    }
});

// Reset formModified flag on successful form submission
const form = document.getElementById('createUserForm');
if (form) {
    form.addEventListener('submit', function() {
        formModified = false;
    });
}

