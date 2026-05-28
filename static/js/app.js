(function () {
    const sidebar = document.querySelector("[data-sidebar]");
    const toggle = document.querySelector("[data-sidebar-toggle]");

    if (window.lucide) {
        window.lucide.createIcons();
    }

    if (toggle && sidebar) {
        toggle.addEventListener("click", function () {
            sidebar.classList.toggle("is-open");
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
