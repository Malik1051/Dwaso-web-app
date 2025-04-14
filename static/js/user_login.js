document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("userLoginForm");


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

            fetch("/user/login", {
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
                        window.location.href = "/products"; // Redirect user to products page
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }
});
