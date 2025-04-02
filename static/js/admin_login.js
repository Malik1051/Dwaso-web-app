/*document.addEventListener("DOMContentLoaded", function() {
    const loginButton = document.getElementById("loginBtn");

    if (loginButton) {
        loginButton.addEventListener("click", function(event) {
            // Prevent the form from submitting immediately (optional)
            event.preventDefault();

            // Display an alert
            alert("Login button clicked!");

            // Optionally, submit the form programmatically after the alert
            // document.querySelector("form").submit();
        });
    } else {
        console.error("Login button not found!");
    }
});*/



document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("adminLoginForm");


    // Admin Login Function
    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const usernameOrEmail = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();

            if (!usernameOrEmail || !password) {
                alert("Both fields are required!");
                return;
            }

            const formData = { username: usernameOrEmail, password: password };

            fetch("/admin/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            })
                .then(response => response.json()) // Expect JSON response
                .then(data => {
                    alert(data.message); // Show response message
                    if (data.success) {
                        window.location.href = "/admin/dashboard"; // Redirect to dashboard
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }
});
