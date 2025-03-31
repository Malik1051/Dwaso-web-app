
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

        // Form submission (frontend only for now)
        document.getElementById('productForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Frontend only: Product would be uploaded here');
            this.reset();
            document.getElementById('imagePreview').innerHTML = '';
        });
