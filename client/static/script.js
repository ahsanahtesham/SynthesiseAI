// SynthesiseAI Interactive Functions
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to main content
    const main = document.querySelector('main');
    if (main) {
        main.classList.add('fadeIn');
    }
    
    // Feature card animations
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length > 0) {
        featureCards.forEach((card, index) => {
            // Add slight delay to each card for staggered animation
            setTimeout(() => {
                card.classList.add('fadeIn');
            }, index * 100);
            
            // Add hover effect
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px)';
                this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            });
        });
    }
    
    // Step animations
    const steps = document.querySelectorAll('.step');
    if (steps.length > 0) {
        steps.forEach((step, index) => {
            // Add slight delay to each step for staggered animation
            setTimeout(() => {
                step.classList.add('fadeIn');
            }, index * 150);
            
            // Add hover effect
            step.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px)';
                this.style.boxShadow = '0 12px 25px rgba(0, 0, 0, 0.1)';
                this.style.borderColor = '#B100FF';
            });
            
            step.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                this.style.borderColor = '#e5e0eb';
            });
        });
    }
    
    // Handle auto-refresh for jobs with pending/processing status
    const hasActiveJobs = function() {
        return document.querySelector('.status-pending') !== null || 
               document.querySelector('.status-processing') !== null;
    };
    
    if (hasActiveJobs()) {
        console.log('Active jobs detected, setting up refresh...');
        setTimeout(function() {
            window.location.reload();
        }, 5000);
    }
    
    // Make notifications interactive
    const notifications = document.querySelectorAll('.notification-item.unread');
    notifications.forEach(notification => {
        notification.addEventListener('click', function() {
            this.classList.remove('unread');
            // In a real implementation, you would make an API call here
            // to mark the notification as read in the database
            const notificationId = this.getAttribute('data-id');
            if (notificationId) {
                markNotificationAsRead(notificationId);
            }
        });
    });
    
    // Function to mark notification as read via API
    function markNotificationAsRead(notificationId) {
        fetch(`/notifications/${notificationId}/read`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                console.error('Failed to mark notification as read');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Credit usage calculator for document submission
    const documentTextarea = document.getElementById('document_text');
    const creditInfo = document.querySelector('.credit-info');
    
    if (documentTextarea && creditInfo) {
        documentTextarea.addEventListener('input', function() {
            const wordCount = countWords(this.value);
            let creditsRequired = 1; // Default for short documents
            
            if (wordCount > 2000) {
                creditsRequired = 3; // Long document
            } else if (wordCount > 500) {
                creditsRequired = 2; // Medium document
            }
            
            creditInfo.textContent = `${wordCount} words - ${creditsRequired} credit${creditsRequired !== 1 ? 's' : ''}`;
            creditInfo.style.backgroundColor = '#f0f0ff';
            creditInfo.style.borderLeft = '3px solid #B100FF';
            
            // Update submit button text
            const submitButton = document.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.textContent = `Generate Summary (${creditsRequired} credit${creditsRequired !== 1 ? 's' : ''})`;
            }
        });
        
        // Initial calculation
        if (documentTextarea.value) {
            documentTextarea.dispatchEvent(new Event('input'));
        }
    }
    
    // Count words in a string
    function countWords(text) {
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    }
    
    // Character count for textarea
    const textareas = document.querySelectorAll('textarea[data-show-count]');
    textareas.forEach(textarea => {
        const container = textarea.parentElement;
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.textContent = `0/${textarea.maxLength || 'unlimited'}`;
        container.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            counter.textContent = `${this.value.length}/${this.maxLength || 'unlimited'}`;
        });
    });
    
    // Add a loading animation for pending elements
    const pendingElements = document.querySelectorAll('.text-content.pending');
    pendingElements.forEach(element => {
        const loader = document.createElement('div');
        loader.className = 'loader';
        element.appendChild(loader);
    });
    
    // Password strength meter
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput && document.querySelector('.auth-form')) {
        const strengthMeter = document.createElement('div');
        strengthMeter.className = 'password-strength';
        passwordInput.parentElement.appendChild(strengthMeter);
        
        passwordInput.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            let strengthText = '';
            let strengthClass = '';
            
            if (strength < 3) {
                strengthText = 'Weak';
                strengthClass = 'weak';
            } else if (strength < 6) {
                strengthText = 'Medium';
                strengthClass = 'medium';
            } else {
                strengthText = 'Strong';
                strengthClass = 'strong';
            }
            
            strengthMeter.textContent = strengthText;
            strengthMeter.className = `password-strength ${strengthClass}`;
        });
        
        // Add password strength styles
        const strengthStyles = document.createElement('style');
        strengthStyles.textContent = `
            .password-strength {
                margin-top: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            
            .password-strength.weak {
                color: #EF4444;
            }
            
            .password-strength.medium {
                color: #F59E0B;
            }
            
            .password-strength.strong {
                color: #10B981;
            }
        `;
        document.head.appendChild(strengthStyles);
    }
    
    function calculatePasswordStrength(password) {
        let strength = 0;
        
        // Length check
        if (password.length >= 8) strength += 1;
        if (password.length >= 12) strength += 1;
        
        // Character variety
        if (/[a-z]/.test(password)) strength += 1;
        if (/[A-Z]/.test(password)) strength += 1;
        if (/[0-9]/.test(password)) strength += 1;
        if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
        
        return strength;
    }
    
    // Add pulsing effect to the logo
    const logo = document.querySelector('.logo-container img');
    if (logo) {
        logo.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        logo.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    }
});