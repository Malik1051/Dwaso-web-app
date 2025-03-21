document.addEventListener("DOMContentLoaded", function() {
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
});