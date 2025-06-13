document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("registerForm").addEventListener("submit", function (event) {
        let username = document.getElementById("username").value;
        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;
        let confirmPassword = document.getElementById("confirm_password").value;
        let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        let specialCharPattern = /[^\w\s]/;
        let numberPattern = /\d/;

        // Email format validation
        if (!emailPattern.test(email)) {
            alert("Enter a valid email address.");
            event.preventDefault();
            return;
        }

        // Password validation
        if (password.length < 8) {
            alert("Password must be at least 8 characters long.");
            event.preventDefault();
            return;
        }

        if (!specialCharPattern.test(password)) {
            alert("Password must contain at least one special character.");
            event.preventDefault();
            return;
        }

        if (!numberPattern.test(password)) {
            alert("Password must contain at least one number.");
            event.preventDefault();
            return;
        }

        // Confirm password match
        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            event.preventDefault();
            return;
        }
    });
});
