from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.urls import reverse
from .models import Product, Categoria
from .forms import ProductForm, CategoriaForm
from django.core.paginator import Paginator
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch

from datetime import datetime



# -----------------------------------------------------------------------------------------------------------------

def listar_productos(request):
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = Product.objects.filter(categoria_id=categoria_id)
    else:
        productos = Product.objects.all()

    categorias = Categoria.objects.all()  # Obtener todas las categorías

    # Configuración de paginación
    paginator = Paginator(productos, 10)  # Mostrar 10 productos por página
    page_number = request.GET.get('page')  # Obtener el número de página actual
    page_obj = paginator.get_page(page_number)  # Obtener los productos de la página actual

    is_admin = request.user.is_admin
    is_cashier = request.user.is_cashier

    return render(request, 'products/list_products.html', {
        'productos': page_obj,  # Pasar el objeto de página al template
        'categorias': categorias,  # Enviar categorías al template
        'is_admin': is_admin,
        'is_cashier': is_cashier
    })

# -----------------------------------------------------------------------------------------------------------------

def agregar_producto(request):
    # Recuperar datos del formulario desde la sesión
    initial_data = request.session.pop('product_form_data', None)
    form = ProductForm(initial=initial_data)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']

             # Usar el valor de se_vende_fraccionado para determinar la unidad de medida
            if producto.se_vende_fraccionado:
                producto.unidad_medida = 'kg'  # Si se vende fraccionado, unidad es 'kg'
            else:
                producto.unidad_medida = 'unidad'  # Si no se vende fraccionado, unidad es 'unidad'

            producto.save()
            return redirect('listar_productos')
        else:
            # Si el formulario tiene errores, guardar datos en la sesión
            request.session['product_form_data'] = request.POST.dict()

    # Guardar datos en la sesión al redirigir a la creación de categorías
    if request.GET.get('from_category') == 'true':
        form = ProductForm(initial=request.session.get('product_form_data', None))
    
    return render(request, 'products/add_products.html', {'form': form})

# -----------------------------------------------------------------------------------------------------------------

def editar_producto(request, pk):
    producto = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('list_products')
    else:
        form = ProductForm(instance=producto)
    return render(request, 'products/edit_products.html', {'form': form, 'producto': producto})

# -----------------------------------------------------------------------------------------------------------------

def eliminar_producto(request, pk):
    producto = Product.objects.get(pk=pk)

    # Verificar si el usuario es administrador
    if not request.user.is_admin:
        return HttpResponseForbidden("No tienes permiso para eliminar productos.")

    if request.method == 'POST':
        producto.delete()
        return redirect('listar_productos')

    return render(request, 'products/delete_product.html', {'producto': producto})

# -----------------------------------------------------------------------------------------------------------------

def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirige a la vista de agregar producto con el indicador `from_category`
            return redirect(reverse('add_products') + '?from_category=true')
        else:
            messages.error(request, 'Error al crear la categoría. Por favor, inténtalo nuevamente.')
    else:
        form = CategoriaForm()
    
    return render(request, 'products/add_category.html', {'form': form})

# -----------------------------------------------------------------------------------------------------------------

# Vista para listar categorías
def listar_categorias(request):
    categorias = Categoria.objects.all()  # Obtener todas las categorías
    return render(request, 'products/list_category.html', {'categorias': categorias})

# -----------------------------------------------------------------------------------------------------------------

# Vista para editar una categoría
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)

    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre')  # Asumiendo que solo modificas el nombre
        categoria.save()
        messages.success(request, "Categoría actualizada con éxito.")
        return redirect('listar_categorias')

    return render(request, 'products/edit_category.html', {'categoria': categoria})

#-----------------------------------------------------------------------------------------------------------------

def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    # Primero, actualizamos los productos a "Sin categoría" antes de eliminarla
    categoria_sin_categoria = Categoria.objects.get(nombre="Sin categoría")
    productos = Product.objects.filter(categoria=categoria)
    productos.update(categoria=categoria_sin_categoria)
    
    # Luego, eliminamos la categoría
    categoria.delete()
    messages.success(request, "Categoría eliminada con éxito.")
    return redirect('listar_categorias')  # Redirige al listado de categorías

#-----------------------------------------------------------------------------------------------------------------

def imprimir_qr(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))

        # Obtener el producto de la base de datos
        producto = Product.objects.get(id=producto_id)

        # Suponiendo que tienes un nombre de almacén almacenado en tu configuración o base de datos
        nombre_almacen = "La Señora del Salame"  # Esto puede venir de una configuración o modelo

        # Crear el PDF en memoria
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        x, y = 100, 750  # Posición inicial

        # Agregar encabezado con el nombre del almacén, producto y fecha
        c.setFont("Helvetica", 16)
        c.drawString(x, y, f"Almacén: {nombre_almacen}")
        y -= 20
        c.drawString(x, y, f"Producto: {producto.nombre}")
        y -= 20
        c.drawString(x, y, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        y -= 40

        # Ajustar la posición de inicio de los QR más abajo (aumentar el valor de y)
        y -= 80  # Desplaza los QR hacia abajo para que no se superpongan con el encabezado

        # Definir el tamaño de las celdas en la tabla (ajustado a 20mm = 57 puntos)
        cell_width = 57  # Ancho de cada celda en puntos (aproximadamente 20mm)
        cell_height = 65  # Alto de cada celda en puntos (aproximadamente 20mm)

        # Calcular cuántas columnas caben en la página
        page_width = 612  # Ancho de la página (tamaño letter en puntos)
        margins = 20  # Margen izquierdo y derecho
        available_width = page_width - 2 * margins  # Ancho disponible para las celdas
        max_columns = available_width // cell_width  # Número máximo de columnas

        # Número de filas que caben en la página (esto lo dejamos fijo a 8)
        max_rows = 8  # Número de filas que caben en la página

        # Dibujar los QR dentro de las celdas
        for i in range(cantidad):
            row = i // max_columns  # Fila
            col = i % max_columns  # Columna
            qr_x = margins + col * cell_width  # Calcular posición X (con margen izquierdo)
            qr_y = y - (row * cell_height)  # Calcular posición Y (desplazado hacia abajo)

            # Dibujar el marco (rectángulo) alrededor del QR
            c.setStrokeColorRGB(0, 0, 0)  # Color negro para el borde
            c.setLineWidth(2)  # Grosor de línea
            c.rect(qr_x, qr_y, cell_width, cell_height)  # Dibujar el marco

            # Usar el archivo de imagen QR que ya existe para este producto
            qr_image_path = producto.qr_code.path
            c.drawImage(qr_image_path, qr_x, qr_y + 10, width=cell_width, height=cell_height - 10)

            # Dibujar el nombre del producto debajo del QR dentro del mismo marco
            c.setFont("Helvetica", 8)  # Fuente más pequeña
            text_x = qr_x + 2  # Alinear ligeramente hacia la derecha dentro del marco
            text_y = qr_y + 5  # Espacio debajo del QR
            c.drawString(text_x, text_y, producto.nombre[:12])  # Mostrar máximo 12 caracteres para evitar desbordes

        # Finalizar el PDF
        c.showPage()
        c.save()

        # Enviar el PDF como respuesta para que se descargue
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="productos_qr.pdf"'  # Forzar la descarga

        return response

    else:
        # Si no es un POST, mostrar el formulario
        productos = Product.objects.all()
        return render(request, 'products/imprimir_qr.html', {'productos': productos})

