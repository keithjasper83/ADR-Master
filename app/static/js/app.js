// ADR-Workbench JavaScript

// Initialize HTMX events
document.body.addEventListener('htmx:afterSwap', function(event) {
    console.log('Content swapped:', event.detail);
});

document.body.addEventListener('htmx:responseError', function(event) {
    console.error('HTMX error:', event.detail);
    showNotification('Error: ' + event.detail.xhr.statusText, 'error');
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${getNotificationClass(type)}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function getNotificationClass(type) {
    const classes = {
        'success': 'bg-green-500 text-white',
        'error': 'bg-red-500 text-white',
        'warning': 'bg-yellow-500 text-white',
        'info': 'bg-blue-500 text-white'
    };
    return classes[type] || classes['info'];
}

// Markdown preview
function toggleMarkdownPreview(textareaId, previewId) {
    const textarea = document.getElementById(textareaId);
    const preview = document.getElementById(previewId);
    
    if (preview.classList.contains('hidden')) {
        // Show preview
        fetch('/api/markdown/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: textarea.value })
        })
        .then(response => response.json())
        .then(data => {
            preview.innerHTML = data.html;
            preview.classList.remove('hidden');
            textarea.classList.add('hidden');
        })
        .catch(error => {
            showNotification('Failed to generate preview', 'error');
        });
    } else {
        // Show editor
        preview.classList.add('hidden');
        textarea.classList.remove('hidden');
    }
}

// Form validation
function validateADRForm(form) {
    const title = form.querySelector('[name="title"]').value;
    const context = form.querySelector('[name="context"]').value;
    const decision = form.querySelector('[name="decision"]').value;
    
    if (title.length < 10) {
        showNotification('Title must be at least 10 characters', 'error');
        return false;
    }
    
    if (context.length < 50) {
        showNotification('Context must be at least 50 characters', 'error');
        return false;
    }
    
    if (decision.length < 50) {
        showNotification('Decision must be at least 50 characters', 'error');
        return false;
    }
    
    return true;
}

// Auto-save functionality
let autoSaveTimer = null;

function enableAutoSave(form, saveUrl, interval = 30000) {
    clearInterval(autoSaveTimer);
    
    autoSaveTimer = setInterval(() => {
        const formData = new FormData(form);
        
        fetch(saveUrl, {
            method: 'PUT',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                showNotification('Auto-saved', 'success');
            }
        })
        .catch(error => {
            console.error('Auto-save failed:', error);
        });
    }, interval);
}

// Export functions
window.ADRWorkbench = {
    showNotification,
    toggleMarkdownPreview,
    validateADRForm,
    enableAutoSave
};
