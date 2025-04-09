// Wait for DOM to be loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add confirmation dialog for logout
    const logoutLink = document.querySelector('a[href="/logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to logout?')) {
                event.preventDefault();
            }
        });
    }
});