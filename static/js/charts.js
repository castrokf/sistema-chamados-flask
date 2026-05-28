(function () {
    if (!window.Chart) {
        return;
    }

    const lineCanvas = document.querySelector("[data-chart-period]");
    const statusCanvas = document.querySelector("[data-chart-status]");

    if (!lineCanvas && !statusCanvas) {
        return;
    }

    fetch("/api/dashboard/stats")
        .then(function (response) {
            return response.json();
        })
        .then(function (stats) {
            if (lineCanvas) {
                new Chart(lineCanvas, {
                    type: "line",
                    data: {
                        labels: stats.period.labels,
                        datasets: [{
                            label: "Chamados",
                            data: stats.period.values,
                            borderColor: "#0f766e",
                            backgroundColor: "rgba(15, 118, 110, 0.12)",
                            tension: 0.38,
                            fill: true,
                            pointRadius: 3
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    precision: 0
                                }
                            }
                        }
                    }
                });
            }

            if (statusCanvas) {
                new Chart(statusCanvas, {
                    type: "doughnut",
                    data: {
                        labels: stats.status.labels,
                        datasets: [{
                            data: stats.status.values,
                            backgroundColor: [
                                "#f59e0b",
                                "#2563eb",
                                "#16a34a",
                                "#7c3aed",
                                "#0f766e"
                            ],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        cutout: "68%",
                        plugins: {
                            legend: {
                                position: "bottom"
                            }
                        }
                    }
                });
            }
        })
        .catch(function () {
            // Mantém a página de relatórios funcional mesmo se a API estiver indisponível.
        });
})();
