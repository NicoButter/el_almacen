// Gráfico de productos por categoría
document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('categoriesChart');
    if (!ctx) return;

    const dataEl = document.getElementById('category-data');
    if (!dataEl) return;

    const payload = JSON.parse(dataEl.textContent);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: payload.labels,
            datasets: [{
                label: 'Productos',
                data: payload.data,
                backgroundColor: 'rgba(127,60,255,0.45)',
                borderColor: '#7f3cff',
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
});
