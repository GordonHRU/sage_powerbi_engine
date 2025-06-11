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
    
    // Initialize searchable dropdowns
    function initSearchableDropdowns() {
        document.querySelectorAll('.searchable-dropdown').forEach(dropdown => {
            const searchInput = dropdown.querySelector('.searchable-input');
            const hiddenInput = dropdown.querySelector('input[type="hidden"]');
            const dropdownList = dropdown.querySelector('.dropdown-list');
            const items = dropdownList.querySelectorAll('li');
            
            console.log('Initializing dropdown:', dropdown.dataset.field); // Debug
            
            // Show dropdown when input is clicked or focused
            searchInput.addEventListener('focus', function() {
                console.log('Input focused, showing dropdown'); // Debug
                dropdown.classList.add('show');
                dropdownList.classList.add('show');
                showAllItems();
            });
            
            searchInput.addEventListener('click', function() {
                console.log('Input clicked, showing dropdown'); // Debug
                dropdown.classList.add('show');
                dropdownList.classList.add('show');
                showAllItems();
            });
            
            // Filter items when typing
            searchInput.addEventListener('input', function() {
                const filter = this.value.toLowerCase();
                console.log('Filtering with:', filter); // Debug
                let hasVisibleItems = false;
                
                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(filter)) {
                        item.style.display = 'block';
                        item.classList.remove('hidden');
                        hasVisibleItems = true;
                    } else {
                        item.style.display = 'none';
                        item.classList.add('hidden');
                    }
                });
                
                console.log('Has visible items:', hasVisibleItems); // Debug
                
                // Always show dropdown when typing
                dropdown.classList.add('show');
                dropdownList.classList.add('show');
                
                // Clear hidden input value when typing (unless exact match)
                const exactMatch = Array.from(items).find(item => 
                    item.textContent.toLowerCase() === filter.toLowerCase()
                );
                
                if (exactMatch) {
                    hiddenInput.value = exactMatch.getAttribute('data-value');
                } else {
                    hiddenInput.value = '';
                }
            });
            
            // Handle item selection
            items.forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const value = this.getAttribute('data-value');
                    const text = this.textContent;
                    
                    console.log('Item selected:', value, text); // Debug
                    
                    searchInput.value = text;
                    hiddenInput.value = value;
                    
                    hideDropdown();
                    
                    // Clear any validation errors
                    if (hiddenInput.classList.contains('is-invalid')) {
                        hideError(hiddenInput);
                    }
                });
            });
            
            // Show all items
            function showAllItems() {
                items.forEach(item => {
                    item.style.display = 'block';
                    item.classList.remove('hidden');
                });
            }
            
            // Hide dropdown
            function hideDropdown() {
                dropdown.classList.remove('show');
                dropdownList.classList.remove('show');
            }
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    hideDropdown();
                }
            });
            
            // Handle keyboard navigation (optional enhancement)
            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                    e.preventDefault();
                    // Could add keyboard navigation here if needed
                }
                if (e.key === 'Escape') {
                    hideDropdown();
                }
            });
        });
    }
    
    // Initialize searchable dropdowns
    initSearchableDropdowns();
    
    // Remove the old searchable select function
    // document.querySelectorAll('.searchable-select').forEach(makeSearchableSelect);
    
    // Real-time validation
    function validateField(field) {
        const value = field.value.trim();
        
        if (field.id === 'triggerHour' || field.id === 'triggerMinute') {
            const hour = document.getElementById('triggerHour').value;
            const minute = document.getElementById('triggerMinute').value;
            
            // Validate hour
            const hourNum = parseInt(hour);
            const isHourValid = hour !== '' && !isNaN(hourNum) && hourNum >= 0 && hourNum <= 23;
            
            // Validate minute
            const minuteNum = parseInt(minute);
            const isMinuteValid = minute !== '' && !isNaN(minuteNum) && minuteNum >= 0 && minuteNum <= 59;
            
            // Handle hour validation
            if (!isHourValid) {
                if (hour === '') {
                    showError(document.getElementById('triggerHour'), 'Please enter an hour.');
                } else {
                    showError(document.getElementById('triggerHour'), 'Hour must be between 0 and 23.');
                }
            } else {
                hideError(document.getElementById('triggerHour'));
            }
            
            // Handle minute validation
            if (!isMinuteValid) {
                if (minute === '') {
                    showError(document.getElementById('triggerMinute'), 'Please enter a minute.');
                } else {
                    showError(document.getElementById('triggerMinute'), 'Minute must be between 0 and 59.');
                }
            } else {
                hideError(document.getElementById('triggerMinute'));
            }
            
            return isHourValid && isMinuteValid;
        }
        
        const isValid = value !== '';
        
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
        
        // Check if this is a hidden input from searchable dropdown
        if (field.type === 'hidden') {
            const dropdown = field.closest('.searchable-dropdown');
            if (dropdown) {
                const searchInput = dropdown.querySelector('.searchable-input');
                if (searchInput) {
                    // Track focus on the search input instead
                    searchInput.addEventListener('focus', function() {
                        hasBeenFocused = true;
                    });
                    
                    searchInput.addEventListener('blur', function() {
                        if (hasBeenFocused) {
                            setTimeout(() => validateField(field), 200);
                        }
                    });
                    
                    // Validate when value changes
                    const observer = new MutationObserver(function() {
                        if (hasBeenFocused) {
                            validateField(field);
                        }
                    });
                    observer.observe(field, { attributes: true, attributeFilter: ['value'] });
                    
                    return; // Skip the regular validation setup for hidden fields
                }
            }
        }
        
        // Regular validation setup for other fields
        field.addEventListener('focus', function() {
            hasBeenFocused = true;
        });
        
        field.addEventListener('blur', function() {
            if (hasBeenFocused) {
                validateField(field);
            }
        });
        
        field.addEventListener('input', function() {
            if (hasBeenFocused && field.classList.contains('is-invalid')) {
                validateField(field);
            }
        });
        
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