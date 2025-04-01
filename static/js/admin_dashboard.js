// Load products when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
});

// Function to load and display products
function loadProducts() {
    fetch('/admin/products')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const productGrid = document.querySelector('.product-grid');
                productGrid.innerHTML = ''; // Clear existing products
                
                data.products.forEach(product => {
                    const productCard = createProductCard(product);
                    productGrid.appendChild(productCard);
                });
            } else {
                console.error('Error loading products:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Function to create product card
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.innerHTML = `
        <img src="/static/uploads/${product.image_path}" alt="${product.name}">
        <h3>${product.name}</h3>
        <p>KES ${product.price.toLocaleString()}</p>
        <p class="description">${product.description}</p>
    `;
    return card;
}

// Image preview functionality
document.getElementById('productImage').addEventListener('change', function(e) {
    const preview = document.getElementById('imagePreview');
    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
    }

    if (file) {
        reader.readAsDataURL(file);
    }
});

// Form submission
document.getElementById('productForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    // Disable button and show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    
    fetch('/admin/upload-product', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Product uploaded successfully!');
            this.reset();
            document.getElementById('imagePreview').innerHTML = '';
            loadProducts(); // Reload products grid
        } else {
            alert('Error uploading product: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading the product');
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    });
});
