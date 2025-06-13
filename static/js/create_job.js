document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createJobForm');
    const cancelBtn = document.getElementById('cancelBtn');
    const createBtn = document.getElementById('createBtn');
    
    // Error messages for each field
    const errorMessages = {
        'jobName': 'Please provide a valid job name.',
        'programId': 'Please select a valid program ID.',
        'propertiesName': 'Please select a valid properties name.',
        'triggerFrequency': 'Please select a trigger frequency.',
        'triggerDay': 'Please select a day of the week.',
        'triggerDate': 'Please select a day of the month.',
        'triggerHour': 'Please select an hour.',
        'triggerMinute': 'Please select a minute.'
    };
    
    // Data for dropdowns
    const dropdownData = {
        programId: [
            { value: '1', text: 'PROG_001 - Sales Report Generator' },
            { value: '2', text: 'PROG_002 - KPI Dashboard Builder' },
            { value: '3', text: 'PROG_003 - Financial Report Engine' },
            { value: '4', text: 'PROG_004 - Business Analytics Tool' },
            { value: '5', text: 'PROG_005 - Customer Data Processor' },
            { value: '6', text: 'PROG_006 - Inventory Tracker' },
            { value: '7', text: 'PROG_007 - Performance Monitor' },
            { value: '8', text: 'PROG_008 - Marketing Analytics' },
            { value: '9', text: 'PROG_009 - HR Dashboard' },
            { value: '10', text: 'PROG_010 - Supply Chain Analyzer' }
        ],
        propertiesName: [
            { value: 'SalesReportConfig', text: 'SalesReportConfig' },
            { value: 'KPIDashboardSettings', text: 'KPIDashboardSettings' },
            { value: 'FinancialReportTemplate', text: 'FinancialReportTemplate' },
            { value: 'QuarterlyAnalysisConfig', text: 'QuarterlyAnalysisConfig' },
            { value: 'CustomerDataProcessing', text: 'CustomerDataProcessing' },
            { value: 'InventoryTrackingSettings', text: 'InventoryTrackingSettings' },
            { value: 'PerformanceMetricsConfig', text: 'PerformanceMetricsConfig' },
            { value: 'MarketingCampaignSettings', text: 'MarketingCampaignSettings' },
            { value: 'HRAnalyticsTemplate', text: 'HRAnalyticsTemplate' },
            { value: 'SupplyChainConfiguration', text: 'SupplyChainConfiguration' },
            { value: 'DataWarehouseSettings', text: 'DataWarehouseSettings' },
            { value: 'ReportingEngineConfig', text: 'ReportingEngineConfig' }
        ]
    };
    
    // Helper function to generate cron expression
    function generateCronExpression(frequency, day, date, hour, minute) {
        try {
            if (frequency === 'Daily') {
                return `${minute} ${hour} * * *`;
            } else if (frequency === 'Weekly') {
                // Convert day name to number (Monday=1, Sunday=0)
                const dayMapping = {
                    'Monday': '1', 'Tuesday': '2', 'Wednesday': '3', 'Thursday': '4',
                    'Friday': '5', 'Saturday': '6', 'Sunday': '0'
                };
                const dayNum = dayMapping[day];
                if (!dayNum && dayNum !== '0') {
                    return null;
                }
                return `${minute} ${hour} * * ${dayNum}`;
            } else if (frequency === 'Monthly') {
                return `${minute} ${hour} ${date} * *`;
            } else {
                return null;
            }
        } catch (error) {
            return null;
        }
    }
    
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
        hideError(field);
        field.classList.add('is-invalid');
        
        const dropdown = field.closest('.searchable-dropdown');
        if (dropdown) {
            const searchInput = dropdown.querySelector('.searchable-input');
            if (searchInput) {
                searchInput.classList.add('is-invalid');
            }
            const errorDiv = createErrorMessage(field.id, message);
            dropdown.parentNode.insertBefore(errorDiv, dropdown.nextSibling);
        } else {
            const errorDiv = createErrorMessage(field.id, message);
            field.parentNode.appendChild(errorDiv);
        }
    }
    
    // Function to hide error message
    function hideError(field) {
        field.classList.remove('is-invalid');
        
        const dropdown = field.closest('.searchable-dropdown');
        if (dropdown) {
            const searchInput = dropdown.querySelector('.searchable-input');
            if (searchInput) {
                searchInput.classList.remove('is-invalid');
            }
        }
        
        const existingError = document.getElementById(field.id + '-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // Initialize searchable dropdowns
    function initSearchableDropdowns() {
        document.querySelectorAll('.searchable-dropdown').forEach(dropdown => {
            const fieldName = dropdown.getAttribute('data-field');
            const searchInput = dropdown.querySelector('.searchable-input');
            const hiddenInput = dropdown.querySelector('input[type="hidden"]');
            const dropdownArrow = dropdown.querySelector('.dropdown-arrow');
            const dropdownList = dropdown.querySelector('.dropdown-list');
            
            if (!searchInput || !hiddenInput || !dropdownArrow || !dropdownList) {
                return;
            }
            
            // Clear and populate dropdown
            dropdownList.innerHTML = '';
            const data = dropdownData[fieldName];
            
            if (!data) {
                return;
            }
            
            data.forEach(item => {
                const li = document.createElement('li');
                li.setAttribute('data-value', item.value);
                li.textContent = item.text;
                li.setAttribute('tabindex', '-1');
                dropdownList.appendChild(li);
            });
            
            // Show/hide functions
            function showDropdown() {
                // Hide other dropdowns
                document.querySelectorAll('.searchable-dropdown.show').forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('show');
                    }
                });
                dropdown.classList.add('show');
            }
            
            function hideDropdown() {
                dropdown.classList.remove('show');
            }
            
            // Arrow click event
            dropdownArrow.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                if (dropdown.classList.contains('show')) {
                    hideDropdown();
                } else {
                    showDropdown();
                    searchInput.focus();
                }
            });
            
            // Input focus events
            searchInput.addEventListener('focus', showDropdown);
            searchInput.addEventListener('click', showDropdown);
            
            // Search functionality
            searchInput.addEventListener('input', function() {
                const filter = this.value.toLowerCase().trim();
                const items = Array.from(dropdownList.children);
                
                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    const value = item.getAttribute('data-value').toLowerCase();
                    
                    if (filter === '' || text.includes(filter) || value.includes(filter)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                // Check for exact match
                const exactMatch = items.find(item => {
                    if (item.style.display === 'none') return false;
                    const text = item.textContent.toLowerCase();
                    const value = item.getAttribute('data-value').toLowerCase();
                    return text === filter || value === filter;
                });
                
                hiddenInput.value = exactMatch ? exactMatch.getAttribute('data-value') : '';
                
                showDropdown();
                
                if (hiddenInput.classList.contains('is-invalid')) {
                    hideError(hiddenInput);
                }
            });
            
            // Item selection
            dropdownList.addEventListener('click', function(e) {
                const item = e.target.closest('li');
                if (!item) return;
                
                e.preventDefault();
                e.stopPropagation();
                
                const value = item.getAttribute('data-value');
                const text = item.textContent;
                
                searchInput.value = text;
                hiddenInput.value = value;
                
                hideDropdown();
                
                if (hiddenInput.classList.contains('is-invalid')) {
                    hideError(hiddenInput);
                }
            });
            
            // Close when clicking outside
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    hideDropdown();
                }
            });
            
            // Keyboard navigation
            searchInput.addEventListener('keydown', function(e) {
                const visibleItems = Array.from(dropdownList.children).filter(item => item.style.display !== 'none');
                
                if (e.key === 'Escape') {
                    hideDropdown();
                    this.blur();
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    showDropdown();
                    if (visibleItems.length > 0) {
                        visibleItems[0].focus();
                    }
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    if (visibleItems.length === 1) {
                        const item = visibleItems[0];
                        searchInput.value = item.textContent;
                        hiddenInput.value = item.getAttribute('data-value');
                        hideDropdown();
                        
                        if (hiddenInput.classList.contains('is-invalid')) {
                            hideError(hiddenInput);
                        }
                    }
                }
            });
        });
    }
    
    // Initialize dropdowns
    initSearchableDropdowns();
    
    // Handle dynamic frequency fields
    function handleFrequencyChange() {
        const frequency = document.getElementById('triggerFrequency').value;
        const triggerDayContainer = document.getElementById('triggerDayContainer');
        const triggerDateContainer = document.getElementById('triggerDateContainer');
        const triggerDayField = document.getElementById('triggerDay');
        const triggerDateField = document.getElementById('triggerDate');
        
        // Hide all conditional fields first
        triggerDayContainer.style.display = 'none';
        triggerDateContainer.style.display = 'none';
        
        // Remove required attribute from both
        triggerDayField.removeAttribute('required');
        triggerDateField.removeAttribute('required');
        
        // Clear values
        triggerDayField.value = '';
        triggerDateField.value = '';
        
        // Clear any existing errors
        hideError(triggerDayField);
        hideError(triggerDateField);
        
        // Show appropriate field based on frequency
        if (frequency === 'Weekly') {
            triggerDayContainer.style.display = 'block';
            triggerDayField.setAttribute('required', 'required');
        } else if (frequency === 'Monthly') {
            triggerDateContainer.style.display = 'block';
            triggerDateField.setAttribute('required', 'required');
        }
    }
    
    // Add event listener to trigger frequency
    const triggerFrequency = document.getElementById('triggerFrequency');
    if (triggerFrequency) {
        triggerFrequency.addEventListener('change', handleFrequencyChange);
    }
    
    // Validation function
    function validateField(field) {
        const value = field.value.trim();
        
        if (field.id === 'triggerHour' || field.id === 'triggerMinute') {
            const hour = document.getElementById('triggerHour').value;
            const minute = document.getElementById('triggerMinute').value;
            
            const hourNum = parseInt(hour);
            const isHourValid = hour !== '' && !isNaN(hourNum) && hourNum >= 0 && hourNum <= 23;
            
            const minuteNum = parseInt(minute);
            const isMinuteValid = minute !== '' && !isNaN(minuteNum) && minuteNum >= 0 && minuteNum <= 59;
            
            if (!isHourValid) {
                if (hour === '') {
                    showError(document.getElementById('triggerHour'), 'Please enter an hour.');
                } else {
                    showError(document.getElementById('triggerHour'), 'Hour must be between 0 and 23.');
                }
            } else {
                hideError(document.getElementById('triggerHour'));
            }
            
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
        
        // Special validation for conditional fields
        if (field.id === 'triggerDay') {
            const frequency = document.getElementById('triggerFrequency').value;
            const isRequired = frequency === 'Weekly';
            
            if (isRequired && value === '') {
                showError(field, errorMessages[field.id]);
                return false;
            } else {
                hideError(field);
                return true;
            }
        }
        
        if (field.id === 'triggerDate') {
            const frequency = document.getElementById('triggerFrequency').value;
            const isRequired = frequency === 'Monthly';
            
            if (isRequired && value === '') {
                showError(field, errorMessages[field.id]);
                return false;
            } else {
                hideError(field);
                return true;
            }
        }
        
        // Regular validation for other fields
        const isValid = value !== '';
        
        if (!isValid) {
            showError(field, errorMessages[field.id]);
        } else {
            hideError(field);
        }
        
        return isValid;
    }
    
    // Add validation to required fields
    const requiredFields = form.querySelectorAll('[required], #triggerDay, #triggerDate');
    requiredFields.forEach(field => {
        let hasBeenBlurred = false;
        
        if (field.type === 'hidden') {
            const dropdown = field.closest('.searchable-dropdown');
            if (dropdown) {
                const searchInput = dropdown.querySelector('.searchable-input');
                if (searchInput) {
                    searchInput.addEventListener('focus', function() {
                        if (hasBeenBlurred && field.classList.contains('is-invalid')) {
                            hideError(field);
                        }
                    });
                    
                    searchInput.addEventListener('input', function() {
                        if (hasBeenBlurred && field.classList.contains('is-invalid')) {
                            if (field.value.trim() !== '') {
                                hideError(field);
                            }
                        }
                    });
                    
                    searchInput.addEventListener('blur', function() {
                        hasBeenBlurred = true;
                        setTimeout(() => {
                            if (!dropdown.contains(document.activeElement)) {
                                validateField(field);
                            }
                        }, 150);
                    });
                    
                    return;
                }
            }
        }
        
        field.addEventListener('focus', function() {
            if (hasBeenBlurred && field.classList.contains('is-invalid')) {
                hideError(field);
            }
        });
        
        field.addEventListener('input', function() {
            if (hasBeenBlurred && field.classList.contains('is-invalid')) {
                if (field.value.trim() !== '') {
                    hideError(field);
                }
            }
        });
        
        field.addEventListener('blur', function() {
            hasBeenBlurred = true;
            validateField(field);
        });
        
        if (field.tagName === 'SELECT') {
            field.addEventListener('change', function() {
                if (hasBeenBlurred) {
                    validateField(field);
                }
            });
        }
    });
    
    // UPDATED FORM SUBMISSION - JSON VERSION
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Always prevent default form submission
            
            // Get all currently required fields (including conditional ones)
            const allFields = form.querySelectorAll('[required]');
            const conditionalFields = [];
            
            // Add conditional fields if they should be required
            const frequency = document.getElementById('triggerFrequency').value;
            if (frequency === 'Weekly') {
                conditionalFields.push(document.getElementById('triggerDay'));
            } else if (frequency === 'Monthly') {
                conditionalFields.push(document.getElementById('triggerDate'));
            }
            
            // Combine all fields that need validation
            const fieldsToValidate = [...allFields, ...conditionalFields];
            let isFormValid = true;
            
            fieldsToValidate.forEach(field => {
                if (!validateField(field)) {
                    isFormValid = false;
                }
            });
            
            if (!isFormValid) {
                const firstInvalidField = form.querySelector('.is-invalid');
                if (firstInvalidField) {
                    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalidField.focus();
                }
                return false;
            }
            
            if (createBtn) {
                createBtn.disabled = true;
                createBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Creating...';
            }
            
            // Collect form data
            const jobName = document.getElementById('jobName').value.trim();
            const programId = document.getElementById('programId').value.trim();
            const triggerFrequency = document.getElementById('triggerFrequency').value;
            const triggerDay = document.getElementById('triggerDay').value;
            const triggerDate = document.getElementById('triggerDate').value;
            const triggerHour = document.getElementById('triggerHour').value;
            const triggerMinute = document.getElementById('triggerMinute').value;
            
            // Generate cron expression
            const cronExpression = generateCronExpression(
                triggerFrequency,
                triggerDay,
                triggerDate,
                parseInt(triggerHour),
                parseInt(triggerMinute)
            );
            
            if (!cronExpression) {
                alert('Failed to generate schedule expression');
                if (createBtn) {
                    createBtn.disabled = false;
                    createBtn.innerHTML = 'Create';
                }
                return false;
            }
            
            // Prepare JSON payload for the existing create_job function
            const jsonData = {
                job_name: jobName,
                program_id: programId,
                cron_expression: cronExpression,
                enabled: true
            };
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Submit via JSON to the existing create_job function
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(jsonData)
            })
            .then(response => {
                
                if (!response.ok) {
                    return response.json().then(err => {
                        return Promise.reject(err);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    alert('Job created successfully!');
                    window.location.href = document.querySelector('a[href*="job_scheduler"]')?.href || '/job-scheduler/';
                } else {
                    alert('Error: ' + (data.message || 'Failed to create job'));
                }
            })
            .catch(error => {
                if (error.message) {
                    alert('Error: ' + error.message);
                } else {
                    alert('An error occurred while creating the job.');
                }
            })
            .finally(() => {
                // Re-enable the button
                if (createBtn) {
                    createBtn.disabled = false;
                    createBtn.innerHTML = 'Create';
                }
            });
            
            return false;
        });
    }
    
    // Cancel button
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to cancel? All unsaved changes will be lost.')) {
                window.location.href = document.querySelector('a[href*="job_scheduler"]')?.href || '/job-scheduler/';
            }
        });
    }
});