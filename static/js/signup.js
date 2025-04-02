document.addEventListener("DOMContentLoaded", function() {
    // Password toggle functionality
    const togglePassword = document.querySelectorAll('.toggle-password');
    togglePassword.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    });

    // Form submission
    document.getElementById('adminSignupForm').addEventListener('submit', function(e) {
        e.preventDefault();

        // Clear previous errors
        document.getElementById('nameError').textContent = '';
        document.getElementById('emailError').textContent = '';
        document.getElementById('passwordError').textContent = '';
        document.getElementById('confirmError').textContent = '';
        
        // Get form values
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // Validation
        let isValid = true;
        
        if (username.length < 3) {
            document.getElementById('nameError').textContent = 'Username must be at least 3 characters';
            isValid = false;
        }
        
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            document.getElementById('emailError').textContent = 'Please enter a valid email address';
            isValid = false;
        }
        
        if (password.length < 6) {
            document.getElementById('passwordError').textContent = 'Password must be at least 6 characters';
            isValid = false;
        }
        
        if (password !== confirmPassword) {
            document.getElementById('confirmError').textContent = 'Passwords do not match';
            isValid = false;
        }
        
        if (isValid) {
            // Prepare data for backend
            const formData = {
                username: username,
                email: email,
                password: password
            };

            // Show loading state
            const submitButton = document.getElementById('signupBtn');
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
            submitButton.disabled = true;

            // Send data to Flask backend
            fetch('/admin/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    alert(data.message);
                    // Reset form
                    document.getElementById('adminSignupForm').reset();
                    // Redirect to login
                    window.location.href = "/ad_login";
                } else {
                    // Show error message
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            })
            .finally(() => {
                // Reset button state
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
            });
        }
    });

    // Add input event listeners for real-time validation
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            // Clear error when user starts typing
            const errorElement = this.parentElement.nextElementSibling;
            if (errorElement && errorElement.classList.contains('error')) {
                errorElement.textContent = '';
            }
        });
    });
});