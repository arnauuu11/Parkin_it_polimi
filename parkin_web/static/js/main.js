// Main JavaScript for Parkin-it

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile menu if open
                if (navLinks && navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                }
            }
        });
    });
    
    // Form Validation for Contact Form
    const contactForm = document.querySelector('.contact-form form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple validation
            let isValid = true;
            const formInputs = this.querySelectorAll('input, textarea');
            
            formInputs.forEach(input => {
                if (input.hasAttribute('required') && input.value.trim() === '') {
                    isValid = false;
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
                
                if (input.type === 'email' && input.value.trim() !== '') {
                    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailPattern.test(input.value.trim())) {
                        isValid = false;
                        input.classList.add('error');
                    }
                }
            });
            
            if (isValid) {
                // Simulate form submission
                const submitButton = this.querySelector('button[type="submit"]');
                const originalText = submitButton.textContent;
                
                submitButton.disabled = true;
                submitButton.textContent = 'Sending...';
                
                setTimeout(() => {
                    alert('Thank you for your message! We will get back to you soon.');
                    this.reset();
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }, 1500);
            }
        });
    }
});