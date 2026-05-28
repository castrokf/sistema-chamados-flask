(function () {
    const sidebar = document.querySelector("[data-sidebar]");
    const toggle = document.querySelector("[data-sidebar-toggle]");
    const profileMenu = document.querySelector("[data-profile-menu]");
    const profileToggle = document.querySelector("[data-profile-toggle]");

    if (window.lucide) {
        window.lucide.createIcons();
    }

    if (toggle && sidebar) {
        toggle.addEventListener("click", function () {
            sidebar.classList.toggle("is-open");
        });
    }

    if (profileMenu && profileToggle) {
        profileToggle.addEventListener("click", function (event) {
            event.stopPropagation();
            const isOpen = profileMenu.classList.toggle("is-open");
            profileToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });

        document.addEventListener("click", function (event) {
            if (!profileMenu.contains(event.target)) {
                profileMenu.classList.remove("is-open");
                profileToggle.setAttribute("aria-expanded", "false");
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                profileMenu.classList.remove("is-open");
                profileToggle.setAttribute("aria-expanded", "false");
            }
        });
    }

    setTimeout(function () {
        document.querySelectorAll(".alert").forEach(function (alerta) {
            if (window.bootstrap) {
                window.bootstrap.Alert.getOrCreateInstance(alerta).close();
            }
        });
    }, 4000);
})();
