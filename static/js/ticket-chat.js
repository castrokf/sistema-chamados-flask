(function () {
    const chat = document.querySelector("[data-ticket-chat]");

    if (!chat) {
        return;
    }

    const ticketId = chat.getAttribute("data-ticket-chat");
    const list = chat.querySelector("[data-chat-list]");
    const form = chat.querySelector("[data-chat-form]");

    function renderMessage(message) {
        const item = document.createElement("div");
        item.className = "chat-message " + message.sender_type;
        item.innerHTML = "<small>" + message.sender_label + " • " + message.created_at + "</small><div></div>";
        item.querySelector("div").textContent = message.message;
        return item;
    }

    function loadMessages() {
        fetch("/chamado/" + ticketId + "/messages")
            .then(function (response) {
                return response.json();
            })
            .then(function (messages) {
                list.innerHTML = "";

                messages.forEach(function (message) {
                    list.appendChild(renderMessage(message));
                });
            });
    }

    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();

            const formData = new FormData(form);

            fetch("/chamado/" + ticketId + "/messages", {
                method: "POST",
                body: formData
            })
                .then(function (response) {
                    if (response.ok) {
                        form.reset();
                        loadMessages();
                    }
                });
        });
    }

    loadMessages();
    window.setInterval(loadMessages, 5000);
})();
