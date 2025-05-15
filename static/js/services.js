// Dummy function for booking service - needs implementation
function bookService(serviceId) {
    alert('Book service with ID: ' + serviceId);
    // TODO: Implement actual service booking logic
}

// Add event listeners for book service buttons
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function() {
            const serviceId = this.getAttribute('data-service-id');
            bookService(serviceId);
        });
    });
});
