document.getElementById('adminSignupForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Clear previous errors
    document.getElementById('nameError').textContent = '';
    document.getElementById('emailError').textContent = '';
    document.getElementById('passwordError').textContent = '';
    document.getElementById('confirmError').textContent = '';
    
    // Get form values
    const name = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Simple validation
    let isValid = true;
    
    if (name.length < 3) {
        document.getElementById('nameError').textContent = 'Name must be at least 3 characters';
        isValid = false;
    }
    
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailPattern.test(email)) {
    document.getElementById('emailError').textContent = 'Please enter a valid email';
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
        // Form is valid - you would typically send data to server here
        alert('Account created successfully!');
        // Prepare data for backend
        const formData = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value
        };
        // Send data to Flask backend
        fetch('/admin/signup', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        })
        .then(response => response.json().catch(() => null)) // Prevent JSON parsing errors
        .then(data => {
            console.log("Response from server:", data);
            if (!data) {
                alert("Invalid server response.");
                return;
            }
            alert(data.message);
            if (data.success) {
                document.getElementById('adminSignupForm').reset();
                window.location.href = "/admin/login";
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        });
        
    }
});

document.addEventListener("DOMContentLoaded", function() {
    console.log("Script loaded"); // Debugging

    const signupBtn = document.getElementById("signupBtn");

    if (signupBtn) {
        signupBtn.addEventListener("click", function(event) {
            event.preventDefault();
            alert("Signup button clicked!");
        });
    } else {
        console.error("Signup button not found!");
    }
});