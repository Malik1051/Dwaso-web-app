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