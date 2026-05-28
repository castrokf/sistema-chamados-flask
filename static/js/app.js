(function () {
    const sidebar = document.querySelector("[data-sidebar]");
    const toggle = document.querySelector("[data-sidebar-toggle]");
    const profileMenu = document.querySelector("[data-profile-menu]");
    const profileToggle = document.querySelector("[data-profile-toggle]");
    const notificationMenu = document.querySelector("[data-notification-menu]");
    const notificationToggle = document.querySelector("[data-notification-toggle]");
    const notificationList = document.querySelector("[data-notification-list]");
    const notificationDot = document.querySelector("[data-notification-dot]");
    const dynamicGreeting = document.querySelector("[data-dynamic-greeting]");

    if (window.lucide) {
        window.lucide.createIcons();
    }

    if (toggle && sidebar) {
        toggle.addEventListener("click", function () {
            sidebar.classList.toggle("is-open");
        });
    }

    function setDynamicGreeting() {
        if (!dynamicGreeting) {
            return;
        }

        const userName = dynamicGreeting.dataset.userName || "usuário";
        const hour = new Date().getHours();
        let greeting = "Boa noite";

        if (hour >= 5 && hour < 12) {
            greeting = "Bom dia";
        } else if (hour >= 12 && hour < 18) {
            greeting = "Boa tarde";
        }

        dynamicGreeting.textContent = `${greeting}, ${userName}. Aqui está o resumo atualizado de hoje.`;
    }

    setDynamicGreeting();
    setInterval(setDynamicGreeting, 60000);

    if (profileMenu && profileToggle) {
        profileToggle.addEventListener("click", function (event) {
            event.stopPropagation();
            const isOpen = profileMenu.classList.toggle("is-open");
            profileToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");

            if (notificationMenu && isOpen) {
                notificationMenu.classList.remove("is-open");
                notificationToggle?.setAttribute("aria-expanded", "false");
            }
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

    function closeNotificationMenu() {
        if (notificationMenu && notificationToggle) {
            notificationMenu.classList.remove("is-open");
            notificationToggle.setAttribute("aria-expanded", "false");
        }
    }

    function renderNotifications(stats) {
        if (!notificationList) {
            return;
        }

        const cards = stats.cards || {};
        const userRole = notificationMenu?.dataset.userRole || "cliente";
        const isTeam = userRole === "admin" || userRole === "suporte";
        const items = [];

        if (cards.abertos > 0) {
            items.push({
                icon: "clock-3",
                title: `${cards.abertos} aguardando primeira análise`,
                text: "Chamados abertos que ainda precisam de leitura inicial.",
                href: isTeam ? "/admin?status=Aberto" : "/meus_chamados"
            });
        }

        if (cards.triagem > 0) {
            items.push({
                icon: "sparkles",
                title: `${cards.triagem} em triagem inteligente`,
                text: "Solicitações sendo qualificadas pelo Assistente Nortia.",
                href: "/triagem-inteligente"
            });
        }

        if (cards.prontos > 0) {
            items.push({
                icon: "badge-check",
                title: `${cards.prontos} prontos para suporte`,
                text: "Demandas já qualificadas para atuação humana.",
                href: "/triagem-inteligente?status=Pronto%20para%20suporte"
            });
        }

        if (!items.length) {
            notificationList.innerHTML = '<div class="notification-empty">Nenhuma pendência crítica no momento.</div>';
            notificationDot?.classList.add("is-hidden");
            return;
        }

        notificationDot?.classList.remove("is-hidden");
        notificationList.innerHTML = items.map(function (item) {
            return `
                <a class="notification-item" href="${item.href}">
                    <span class="notification-item-icon"><i data-lucide="${item.icon}"></i></span>
                    <span>
                        <strong>${item.title}</strong>
                        <span>${item.text}</span>
                    </span>
                </a>
            `;
        }).join("");

        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    if (notificationMenu && notificationToggle) {
        notificationToggle.addEventListener("click", function (event) {
            event.stopPropagation();
            const isOpen = notificationMenu.classList.toggle("is-open");
            notificationToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");

            if (profileMenu && isOpen) {
                profileMenu.classList.remove("is-open");
                profileToggle?.setAttribute("aria-expanded", "false");
            }
        });

        document.addEventListener("click", function (event) {
            if (!notificationMenu.contains(event.target)) {
                closeNotificationMenu();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeNotificationMenu();
            }
        });
    }

    if (notificationList) {
        fetch("/api/dashboard/stats")
            .then(function (response) {
                return response.json();
            })
            .then(renderNotifications)
            .catch(function () {
                notificationList.innerHTML = '<div class="notification-empty">Não foi possível carregar as notificações agora.</div>';
                notificationDot?.classList.add("is-hidden");
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
