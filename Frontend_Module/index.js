document.addEventListener("DOMContentLoaded", function () {
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    const body = document.body;

    // Check if dark mode is enabled in localStorage
    if (localStorage.getItem("dark-mode") === "enabled") {
        body.classList.add("dark-mode");
    }

    darkModeToggle.addEventListener("click", () => {
        body.classList.toggle("dark-mode");

        // Toggle button color
        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("dark-mode", "enabled");
        } else {
            localStorage.setItem("dark-mode", "disabled");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const mainContent = document.getElementById("main-content");
    const sidebarLinks = document.querySelectorAll(".sidebar a");

    function loadPage(page) {
        fetch(`pages/${page}.html`)
            .then(response => response.text())
            .then(data => {
                mainContent.innerHTML = data;
                history.pushState({ page }, "", `#${page}`); // Update URL without reload
            })
            .catch(error => console.error("Error loading page:", error));
    }

    // Load initial page from URL hash or default to 'get-started'
    const initialPage = location.hash ? location.hash.substring(1) : "get-started";
    loadPage(initialPage);

    // Handle sidebar link clicks
    sidebarLinks.forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            const page = this.getAttribute("data-page");

            sidebarLinks.forEach(link => link.classList.remove("active"));
            this.classList.add("active");

            loadPage(page);
        });
    });

    // Handle back/forward browser navigation
    window.addEventListener("popstate", function (event) {
        if (event.state && event.state.page) {
            loadPage(event.state.page);
        }
    });
});
