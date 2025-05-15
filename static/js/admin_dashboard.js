// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and its content
            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
        });
    });

    // Initialize both grids
    loadProducts();
    loadServices();

    // Set up form submissions
    setupProductForm();
    setupServiceForm();
});

// Function to load and display products
function loadProducts() {
    fetch('/admin/products')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const productGrid = document.getElementById('products-grid');
                productGrid.innerHTML = ''; // Clear existing products
                
                data.products.forEach(product => {
                    const productCard = createItemCard(product, 'product');
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

// Function to load and display services
function loadServices() {
    fetch('/admin/services')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const serviceGrid = document.getElementById('services-grid');
                serviceGrid.innerHTML = ''; // Clear existing services
                
                data.services.forEach(service => {
                    const serviceCard = createItemCard(service, 'service');
                    serviceGrid.appendChild(serviceCard);
                });
            } else {
                console.error('Error loading services:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Function to create item card (works for both products and services)
function createItemCard(item, type) {
    const card = document.createElement('div');
    card.className = 'item-card';
    
    let durationInfo = '';
    if (type === 'service' && item.duration) {
        durationInfo = `<p><strong>Duration:</strong> ${item.duration} hours</p>`;
    }
    
    card.innerHTML = `
        <img src="/static/uploads/${item.image_path}" alt="${item.name}">
        <button class="delete-btn" data-id="${item.id}" data-type="${type}">
            <i class="fas fa-trash"></i>
        </button>
        <h3>${item.name}</h3>
        <p class="description">${item.description}</p>
        ${durationInfo}
        <p class="price">KES ${item.price.toLocaleString()}</p>
    `;

    // Add delete functionality
    const deleteBtn = card.querySelector('.delete-btn');
    deleteBtn.addEventListener('click', () => deleteItem(item.id, type));

    return card;
}

// Function to delete an item (product or service)
function deleteItem(id, type) {
    if (!confirm(`Are you sure you want to delete this ${type}?`)) return;

    fetch(`/admin/${type}s/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (type === 'product') {
                loadProducts();
            } else {
                loadServices();
            }
        } else {
            alert(`Error deleting ${type}: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`An error occurred while deleting the ${type}`);
    });
}

// Function to set up product form
function setupProductForm() {
    const productForm = document.getElementById('productForm');
    const productImageInput = document.getElementById('productImage');
    const productImagePreview = document.getElementById('productImagePreview');

    // Image preview
    productImageInput.addEventListener('change', () => {
        previewImage(productImageInput, productImagePreview);
    });

    // Form submission
    productForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmit(this, 'product');
    });
}

// Function to set up service form
function setupServiceForm() {
    const serviceForm = document.getElementById('serviceForm');
    const serviceImageInput = document.getElementById('serviceImage');
    const serviceImagePreview = document.getElementById('serviceImagePreview');

    // Image preview
    serviceImageInput.addEventListener('change', () => {
        previewImage(serviceImageInput, serviceImagePreview);
    });

    // Form submission
    serviceForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmit(this, 'service');
    });
}

// Function to preview image
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Function to handle form submission
function handleFormSubmit(form, type) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    // Disable button and show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    
    fetch(`/admin/upload-${type}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`${type.charAt(0).toUpperCase() + type.slice(1)} uploaded successfully!`);
            form.reset();
            document.getElementById(`${type}ImagePreview`).innerHTML = '';
            if (type === 'product') {
                loadProducts();
            } else {
                loadServices();
            }
        } else {
            alert(`Error uploading ${type}: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`An error occurred while uploading the ${type}`);
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    });
}
