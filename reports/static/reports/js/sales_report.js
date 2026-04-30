// Gráfico de ventas por período
var graficoDatos = JSON.parse(document.getElementById('graficoEtiquetas').textContent) || [];

var chartContainer = document.getElementById('grafico-ventas');
var periodoSeleccionado = (chartContainer && chartContainer.dataset.periodo) ? chartContainer.dataset.periodo : 'Mes';

var datosFiltrados = graficoDatos.filter(function (d) {
    return d.etiqueta === periodoSeleccionado;
});

if (datosFiltrados.length > 0) {
    const labels = datosFiltrados.map(d => d.etiqueta);
    const dataValues = datosFiltrados.map(d => d.total);

    const ctx = chartContainer.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas ($)',
                data: dataValues,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
} else {
    console.log('No hay datos para mostrar en el gráfico.');
}
