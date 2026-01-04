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
    const button = wrapper.querySelector('.signup-password-toggle, .signin-password-toggle, .reset-password-toggle, .change-password-toggle');
    const icon = button ? button.querySelector('.signup-eye-icon, .signin-eye-icon, .reset-eye-icon, .change-eye-icon') : null;
    
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