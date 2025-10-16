document.addEventListener('DOMContentLoaded', () => {
    const categoryElement = document.getElementById('category-data');
    const categoryCanvas = document.getElementById('categoryChart');
    if (categoryElement && categoryCanvas) {
        const payload = JSON.parse(categoryElement.textContent);
        if (payload.labels.length) {
            new Chart(categoryCanvas, {
                type: 'doughnut',
                data: {
                    labels: payload.labels,
                    datasets: [{
                        label: 'Productos',
                        data: payload.data,
                        backgroundColor: [
                            'rgba(127,60,255,0.8)',
                            'rgba(34,211,238,0.8)',
                            'rgba(96,165,250,0.8)',
                            'rgba(251,191,36,0.8)',
                            'rgba(110,231,183,0.8)',
                        ],
                        borderColor: [
                            'rgba(127,60,255,1)',
                            'rgba(34,211,238,1)',
                            'rgba(96,165,250,1)',
                            'rgba(251,191,36,1)',
                            'rgba(110,231,183,1)',
                        ],
                        borderWidth: 2,
                    }]
                },
                options: {
                    plugins: { legend: { display: true, labels: { color: 'rgba(255,255,255,0.8)' } } },
                    responsive: true,
                }
            });
        }
    }

    const stockElement = document.getElementById('stock-data');
    const stockCanvas = document.getElementById('stockChart');
    if (stockElement && stockCanvas) {
        const payload = JSON.parse(stockElement.textContent);
        if (payload.labels.length) {
            new Chart(stockCanvas, {
                type: 'bar',
                data: {
                    labels: payload.labels,
                    datasets: [{
                        label: 'Stock',
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