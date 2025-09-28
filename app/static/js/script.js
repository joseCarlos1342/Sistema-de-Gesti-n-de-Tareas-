// Task Management System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add loading states to forms
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
            }
        });
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('.btn-danger[type="submit"], .delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres eliminar este elemento?')) {
                e.preventDefault();
            }
        });
    });

    // Add smooth scrolling to anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Task quick actions
    var quickActionButtons = document.querySelectorAll('.quick-action');
    quickActionButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var action = this.dataset.action;
            var taskId = this.dataset.taskId;

            if (action && taskId) {
                performQuickAction(action, taskId, this);
            }
        });
    });

    // Search functionality with debounce
    var searchInput = document.getElementById('search');
    if (searchInput) {
        var searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Auto-submit search form after 500ms of no typing
                if (searchInput.value.length >= 3 || searchInput.value.length === 0) {
                    searchInput.closest('form').submit();
                }
            }, 500);
        });
    }

    // Filter form auto-submit
    var filterSelects = document.querySelectorAll('.auto-filter');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    // Add fade-in animation to new elements
    var newElements = document.querySelectorAll('.fade-in');
    newElements.forEach(function(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';

        setTimeout(function() {
            element.style.transition = 'all 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100);
    });
});

// Quick action function for tasks
function performQuickAction(action, taskId, button) {
    var originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

    var url = '';
    var method = 'POST';

    switch(action) {
        case 'toggle':
            url = `/tasks/${taskId}/toggle`;
            break;
        case 'delete':
            if (!confirm('¿Estás seguro de eliminar esta tarea?')) {
                button.disabled = false;
                button.innerHTML = originalText;
                return;
            }
            url = `/tasks/${taskId}/delete`;
            break;
        default:
            button.disabled = false;
            button.innerHTML = originalText;
            return;
    }

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (action === 'delete') {
                // Remove the task row with animation
                var taskRow = button.closest('tr');
                if (taskRow) {
                    taskRow.style.transition = 'all 0.3s ease';
                    taskRow.style.opacity = '0';
                    taskRow.style.transform = 'translateX(-100%)';
                    setTimeout(() => taskRow.remove(), 300);
                }
            } else {
                // Reload the page for other actions
                location.reload();
            }
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Error al realizar la acción', 'error');
            button.disabled = false;
            button.innerHTML = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
        button.disabled = false;
        button.innerHTML = originalText;
    });
}

// Toast notification function
function showToast(message, type = 'info') {
    var toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }

    var toastId = 'toast-' + Date.now();
    var bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';

    var toastHTML = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
            <div class="toast-header ${bgClass} text-white border-0">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                <strong class="me-auto">Sistema de Tareas</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    var toastElement = document.getElementById(toastId);
    var toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });

    toast.show();

    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Form validation helpers
function validateForm(form) {
    var isValid = true;
    var inputs = form.querySelectorAll('input[required], textarea[required], select[required]');

    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Enhanced date picker for due dates
function initializeDatePicker() {
    var dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        var today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);

        input.addEventListener('change', function() {
            var selectedDate = new Date(this.value);
            var today = new Date();
            today.setHours(0, 0, 0, 0);

            if (selectedDate < today) {
                this.classList.add('is-invalid');
                showToast('La fecha no puede ser anterior a hoy', 'error');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
}

// Initialize date picker when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeDatePicker);

// Task statistics update
function updateTaskStats() {
    fetch('/api/tasks/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('total-tasks').textContent = data.total;
                document.getElementById('pending-tasks').textContent = data.pending;
                document.getElementById('completed-tasks').textContent = data.completed;
                document.getElementById('overdue-tasks').textContent = data.overdue;
            }
        })
        .catch(error => console.error('Error updating stats:', error));
}

// Auto-save functionality for form drafts
function initAutoSave() {
    var forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(function(form) {
        var formId = form.dataset.autosave;
        var inputs = form.querySelectorAll('input, textarea, select');

        // Load saved data
        inputs.forEach(function(input) {
            var savedValue = localStorage.getItem(`${formId}-${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });

        // Save data on input
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                localStorage.setItem(`${formId}-${input.name}`, this.value);
            });
        });

        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            inputs.forEach(function(input) {
                localStorage.removeItem(`${formId}-${input.name}`);
            });
        });
    });
}

// Initialize auto-save when DOM is loaded
document.addEventListener('DOMContentLoaded', initAutoSave);

// Export functionality
function exportTasks(format) {
    var url = `/tasks/export?format=${format}`;
    window.open(url, '_blank');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N for new task
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        var newTaskBtn = document.querySelector('[href*="tasks/new"]');
        if (newTaskBtn) {
            newTaskBtn.click();
        }
    }

    // Ctrl/Cmd + F for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        var searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            e.preventDefault();
            searchInput.focus();
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        var modals = document.querySelectorAll('.modal.show');
        modals.forEach(function(modal) {
            var bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
});