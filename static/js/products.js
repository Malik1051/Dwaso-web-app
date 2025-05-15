// Update cart count
function updateCartCount() {
    fetch('/cart/count')
        .then(response => response.json())
        .then(data => {
            document.querySelector('.cart-count').textContent = data.count;
        });
}

// Add to cart function
function addToCart(productId) {
    fetch('/add-to-cart/' + productId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            // Add a success animation
            const button = document.querySelector(`button[data-product-id="${productId}"]`);
            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Load initial cart count and set up event listeners
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    
    // Add event listeners for add to cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            addToCart(productId);
        });
    });
});
