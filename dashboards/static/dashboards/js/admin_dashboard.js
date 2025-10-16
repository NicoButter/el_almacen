document.addEventListener('DOMContentLoaded', () => {
    const salesDataElement = document.getElementById('sales-trend-data');
    const salesCanvas = document.getElementById('salesTrendChart');
    if (salesDataElement && salesCanvas) {
        const payload = JSON.parse(salesDataElement.textContent);
        if (payload.labels.length) {
            new Chart(salesCanvas, {
                type: 'line',
                data: {
                    labels: payload.labels,
                    datasets: [{
                        label: 'Ingresos',
                        data: payload.data,
                        borderColor: '#c084fc',
                        backgroundColor: 'rgba(192,132,252,0.15)',
                        tension: 0.35,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            ticks: { color: 'rgba(255,255,255,0.65)' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        y: {
                            ticks: { color: 'rgba(255,255,255,0.65)' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        }
                    }
                }
            });
        }
    }

    const topProductsElement = document.getElementById('top-products-data');
    const productsCanvas = document.getElementById('topProductsChart');
    if (topProductsElement && productsCanvas) {
        const payload = JSON.parse(topProductsElement.textContent);
        if (payload.labels.length) {
            new Chart(productsCanvas, {
                type: 'bar',
                data: {
                    labels: payload.labels,
                    datasets: [{
                        label: 'Ingresos',
                        data: payload.data,
                        backgroundColor: 'rgba(34,211,238,0.45)',
                        borderColor: '#22d3ee',
                        borderWidth: 1.5,
                        borderRadius: 8,
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            ticks: { color: 'rgba(255,255,255,0.65)' },
                            grid: { display: false }
                        },
                        y: {
                            ticks: { color: 'rgba(255,255,255,0.65)' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        }
                    }
                }
            });
        }
    }
});