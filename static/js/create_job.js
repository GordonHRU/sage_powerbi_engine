document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createJobForm');
    const cancelBtn = document.getElementById('cancelBtn');
    const createBtn = document.getElementById('createBtn');
    
    // Error messages for each field
    const errorMessages = {
        'jobName': 'Please provide a valid job name.',
        'programId': 'Please select a valid program ID.',
        'propertyName': 'Please select a valid property name.',
        'triggerFrequency': 'Please select a trigger frequency.',
        'triggerHour': 'Please select an hour.',
        'triggerMinute': 'Please select a minute.'
    };
    
    // Function to create error message element
    function createErrorMessage(fieldId, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.id = fieldId + '-error';
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.style.color = '#dc3545';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        return errorDiv;
    }
    
    // Function to show error message
    function showError(field, message) {
        // Remove existing error message if any
        hideError(field);
        
        // Add invalid class to field
        field.classList.add('is-invalid');
        
        // Create and insert error message
        const errorDiv = createErrorMessage(field.id, message);
        field.parentNode.appendChild(errorDiv);
    }
    
    // Function to hide error message
    function hideError(field) {
        // Remove invalid class
        field.classList.remove('is-invalid');
        
        // Remove error message element
        const existingError = document.getElementById(field.id + '-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // Add search functionality to searchable selects
    function makeSearchableSelect(selectElement) {
        const options = Array.from(selectElement.options);
        selectElement.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            options.forEach(option => {
                if (option.value === '') return;
                const text = option.textContent.toLowerCase();
                option.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
    
    // Apply search functionality to searchable selects
    document.querySelectorAll('.searchable-select').forEach(makeSearchableSelect);
    
    // Real-time validation
    function validateField(field) {
        const value = field.value.trim();
        const isValid = value !== '';
        
        if (field.id === 'triggerHour' || field.id === 'triggerMinute') {
            const hour = document.getElementById('triggerHour').value;
            const minute = document.getElementById('triggerMinute').value;
            const timeIsValid = hour !== '' && minute !== '';
            
            if (!timeIsValid) {
                if (hour === '') {
                    showError(document.getElementById('triggerHour'), errorMessages['triggerHour']);
                }
                if (minute === '') {
                    showError(document.getElementById('triggerMinute'), errorMessages['triggerMinute']);
                }
            } else {
                hideError(document.getElementById('triggerHour'));
                hideError(document.getElementById('triggerMinute'));
            }
            
            return timeIsValid;
        }
        
        if (!isValid) {
            showError(field, errorMessages[field.id]);
        } else {
            hideError(field);
        }
        
        return isValid;
    }
    
    // Add real-time validation to all required fields
    form.querySelectorAll('[required]').forEach(field => {
        let hasBeenFocused = false;
        
        // Track when field has been focused
        field.addEventListener('focus', function() {
            hasBeenFocused = true;
        });
        
        // Only validate after field has been focused and then blurred
        field.addEventListener('blur', function() {
            if (hasBeenFocused) {
                validateField(field);
            }
        });
        
        // Clear validation errors when user starts typing (after being focused)
        field.addEventListener('input', function() {
            if (hasBeenFocused && field.classList.contains('is-invalid')) {
                validateField(field);
            }
        });
        
        // For select fields, also listen to change events
        if (field.tagName === 'SELECT') {
            field.addEventListener('change', function() {
                if (hasBeenFocused) {
                    validateField(field);
                }
            });
        }
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        // Validate all fields before submission
        const requiredFields = form.querySelectorAll('[required]');
        let isFormValid = true;
        
        requiredFields.forEach(field => {
            if (!validateField(field)) {
                isFormValid = false;
            }
        });
        
        if (!isFormValid) {
            e.preventDefault();
            
            // Scroll to first invalid field
            const firstInvalidField = form.querySelector('.is-invalid');
            if (firstInvalidField) {
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalidField.focus();
            }
            return false;
        }
        
        // If form is valid, show loading state
        createBtn.disabled = true;
        createBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Creating...';
        
        // Let the form submit normally to Django
        return true;
    });
    
    // Cancel button
    cancelBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to cancel? All unsaved changes will be lost.')) {
            window.location.href = document.querySelector('a[href*="job_scheduler"]').href || '/job-scheduler/';
        }
    });
});