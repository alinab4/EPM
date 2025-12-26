// Core JavaScript functionalities for the application
const API_BASE_URL = '/api';
const TOKEN_KEY = 'token';

/**
 * Handles API requests with proper error handling
 * @param {string} endpoint - The API endpoint to call
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {object} body - The request body for POST/PUT requests
 * @returns {Promise<any>} - The JSON response from the API
 */
async function apiRequest(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem(TOKEN_KEY)}`
    };
    const config = { method, headers };
    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.message || 'API request failed');
        }
        return response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Checks for a valid token and redirects to login if not found
 */
function protectPage() {
    if (!localStorage.getItem(TOKEN_KEY)) {
        window.location.href = '/login.html';
    }
}

/**
 * Logs the user out by clearing the token
 */
function logout() {
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = '/login.html';
}

/**
 * Decodes the JWT to extract user information
 * @returns {object|null} - The decoded payload or null if token is invalid
 */
function getCurrentUser() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return null;
    try {
        const decoded = JSON.parse(atob(token.split('.')[1]));
        return decoded;
    } catch (e) {
        console.error('Failed to decode token:', e);
        return null;
    }
}

/**
 * Shows an alert/toast message
 * @param {string} message - The message to show
 * @param {string} type - The type of alert (success, danger, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showAlert(message, type = 'success', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.maxWidth = '400px';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, duration);
}

/**
 * Formats a date string to a readable format
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Formats a number to a specific decimal place
 * @param {number} num - The number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted number
 */
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

/**
 * Gets a badge HTML string based on status
 * @param {string} status - The status to get badge for
 * @returns {string} - HTML badge element
 */
function getStatusBadge(status) {
    const statusMap = {
        'active': 'Active',
        'inactive': 'Inactive',
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'achieved': 'Achieved',
        'not_achieved': 'Not Achieved'
    };
    
    const display = statusMap[status] || status;
    const badgeClass = `badge badge-${status}`;
    return `<span class="${badgeClass}">${display}</span>`;
}

/**
 * Modal utilities
 */
const Modal = {
    open: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    },
    
    close: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    },
    
    closeAll: function() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
};

/**
 * Setup modal close handlers
 */
function setupModalHandlers() {
    // Close modal when clicking the close button
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Close modal when clicking outside the content
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });
}

/**
 * Initializes common page elements
 */
function initializePage() {
    setupModalHandlers();
    
    // Set user info in sidebar if it exists
    const user = getCurrentUser();
    if (user) {
        const nameEl = document.querySelector('.user-name');
        const roleEl = document.querySelector('.user-role');
        if (nameEl) nameEl.textContent = user.name || 'User';
        if (roleEl) roleEl.textContent = user.role || 'Unknown';
    }
}

// Initialize page when DOM is ready
document.addEventListener('DOMContentLoaded', initializePage);

/**
 * Redirects user to the correct dashboard based on their role
 */
function redirectToDashboard() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = '/login.html';
        return;
    }

    switch (user.role) {
        case 'Admin':
            window.location.href = '/admin_dashboard.html';
            break;
        case 'Manager':
            window.location.href = '/manager_dashboard.html';
            break;
        case 'Employee':
            window.location.href = '/employee_dashboard.html';
            break;
        default:
            window.location.href = '/login.html';
    }
}
