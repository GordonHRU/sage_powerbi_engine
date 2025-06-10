document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createJobForm');
    const cancelBtn = document.getElementById('cancelBtn');
    const createBtn = document.getElementById('createBtn');
    
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
            
            document.getElementById('triggerHour').classList.toggle('is-invalid', !timeIsValid);
            document.getElementById('triggerMinute').classList.toggle('is-invalid', !timeIsValid);
            
            return timeIsValid;
        }
        
        field.classList.toggle('is-invalid', !isValid);
        return isValid;
    }
    
    // Add real-time validation to all required fields
    form.querySelectorAll('[required]').forEach(field => {
        field.addEventListener('blur', () => validateField(field));
        field.addEventListener('change', () => validateField(field));
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