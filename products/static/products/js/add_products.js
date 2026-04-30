// Formulario de agregar producto
document.addEventListener('DOMContentLoaded', function () {
    const costoInput = document.getElementById('id_costo');
    const porcentajeInput = document.getElementById('id_porcentaje_ganancia');
    const precioVentaField = document.getElementById('precio_venta');

    function calcularPrecioVenta() {
        const costo = parseFloat(costoInput.value) || 0;
        const porcentaje = parseFloat(porcentajeInput.value) || 0;
        const precioVenta = costo * (1 + (porcentaje / 100));
        precioVentaField.value = precioVenta.toFixed(2);
    }

    if (costoInput && porcentajeInput && precioVentaField) {
        costoInput.addEventListener('input', calcularPrecioVenta);
        porcentajeInput.addEventListener('input', calcularPrecioVenta);
        calcularPrecioVenta();
    }

    // Manejar el cambio de fraccionado
    const seVendeFraccionadoCheckbox = document.getElementById('id_se_vende_fraccionado');
    const stockLabel = document.getElementById('stock-label');

    if (seVendeFraccionadoCheckbox && stockLabel) {
        function actualizarCantidadStock() {
            if (seVendeFraccionadoCheckbox.checked) {
                stockLabel.textContent = 'Cantidad de Stock (kg)';
            } else {
                stockLabel.textContent = 'Cantidad de Stock (unidades)';
            }
        }

        actualizarCantidadStock();
        seVendeFraccionadoCheckbox.addEventListener('change', actualizarCantidadStock);
    }

    // Preview de imagen
    const imagenInput = document.getElementById('id_imagen');
    if (imagenInput) {
        imagenInput.addEventListener('change', function (event) {
            const [file] = event.target.files;
            if (file) {
                console.log('Imagen seleccionada:', file.name);
            }
        });
    }
});
