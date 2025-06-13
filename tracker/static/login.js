document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loginForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        let formData = {
            username: document.getElementById("username").value,
            password: document.getElementById("password").value
        };

        // Function to get CSRF token from cookies
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== "") {
                let cookies = document.cookie.split(";");
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = cookies[i].trim();
                    if (cookie.startsWith(name + "=")) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        let csrftoken = getCookie("csrftoken"); // Fetch CSRF token

        fetch("http://127.0.0.1:8000/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json().then(data => {
            if (!response.ok) {
                throw new Error(data.detail || "Invalid username or password");
            }
            return data;
        }))
        .then(data => {
            alert("Login successful!");
            localStorage.setItem("authToken", data.token); // Store token for future API requests
            window.location.href = "/dashboard/"; // Redirect to dashboard
        })
        .catch(error => {
            document.getElementById("error-message").textContent = error.message;
            document.getElementById("error-message").style.display = "block";
            console.error("Error:", error);
        });
    });
});
