document.addEventListener('DOMContentLoaded', function() {
    // Format Unix timestamps to human-readable form
    formatTimestamps();
    
    // Register event handlers
    registerEventHandlers();
});

function formatTimestamps() {
    // Add a filter to Jinja2 templates in the Flask app for timestamp formatting
    // This JavaScript is a fallback for dynamic content
    const timestamps = document.querySelectorAll('.timestamp');
    
    timestamps.forEach(element => {
        const timestamp = parseInt(element.textContent.trim());
        if (!isNaN(timestamp)) {
            const date = new Date(timestamp * 1000);
            element.textContent = date.toLocaleString();
        }
    });
}

function registerEventHandlers() {
    // Prevent sending to self
    const senderSelects = document.querySelectorAll('select[name="sender"]');
    const recipientSelects = document.querySelectorAll('select[name="recipient"]');
    
    senderSelects.forEach((senderSelect, i) => {
        senderSelect.addEventListener('change', function() {
            const sender = this.value;
            const recipientSelect = recipientSelects[i];
            
            if (recipientSelect) {
                for (let option of recipientSelect.options) {
                    if (option.value === sender) {
                        if (option.selected) {
                            // Select a different recipient
                            const otherOption = [...recipientSelect.options].find(opt => opt.value !== sender);
                            if (otherOption) {
                                otherOption.selected = true;
                            }
                        }
                    }
                }
            }
        });
    });
    
    recipientSelects.forEach((recipientSelect, i) => {
        recipientSelect.addEventListener('change', function() {
            const recipient = this.value;
            const senderSelect = senderSelects[i];
            
            if (senderSelect && recipient === senderSelect.value) {
                alert("Sender and recipient should be different");
            }
        });
    });
    
    // Form validation
    const transactionForms = document.querySelectorAll('form[action="/create_transaction"]');
    
    transactionForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const sender = this.querySelector('select[name="sender"]').value;
            const recipient = this.querySelector('select[name="recipient"]').value;
            
            if (sender === recipient) {
                event.preventDefault();
                alert("Sender and recipient cannot be the same wallet");
                return false;
            }
            
            const amount = parseFloat(this.querySelector('input[name="amount"]').value);
            if (isNaN(amount) || amount <= 0) {
                event.preventDefault();
                alert("Please enter a valid positive amount");
                return false;
            }
            
            return true;
        });
    });
    
    // Auto-refresh for certain pages (optional)
    /*
    const path = window.location.pathname;
    const refreshPaths = ['/blockchain', '/dag', '/transactions'];
    
    if (refreshPaths.includes(path)) {
        setTimeout(() => {
            window.location.reload();
        }, 30000); // Refresh every 30 seconds
    }
    */
}

// Custom function to toggle detailed views
function toggleDetails(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        if (element.style.display === 'none' || element.style.display === '') {
            element.style.display = 'block';
        } else {
            element.style.display = 'none';
        }
    }
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard');
    }, () => {
        alert('Failed to copy');
    });
}
