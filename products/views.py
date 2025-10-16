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
from typing import cast
from django.core.files import File
from django.db.models import Sum, Count
from datetime import datetime



# -----------------------------------------------------------------------------------------------------------------

def listar_productos(request):
    categoria_id = request.GET.get('categoria')
    search_query = request.GET.get('search', '').strip()

    # Filtrar productos por categoría
    if categoria_id:
        productos = Product.objects.filter(categoria_id=categoria_id).order_by('nombre')
    else:
        productos = Product.objects.all().order_by('nombre')

    # Filtrar productos por búsqueda de nombre
    if search_query:
        productos = productos.filter(nombre__icontains=search_query)

    categorias = Categoria.objects.all()  # Obtener todas las categorías

    # Configuración de paginación
    paginator = Paginator(productos, 10)  # Mostrar 10 productos por página
    page_number = request.GET.get('page')  # Obtener el número de página actual
    page_obj = paginator.get_page(page_number)  # Obtener los productos de la página actual

    is_admin = request.user.is_admin
    is_cashier = request.user.is_cashier

    # Calcular métricas para el dashboard
    total_stock = Product.objects.aggregate(total=Sum('cantidad_stock'))['total'] or 0
    low_stock_count = Product.objects.filter(cantidad_stock__lt=10).count()
    total_value = sum(producto.precio_venta * producto.cantidad_stock for producto in Product.objects.all())

    # Datos para gráfico de productos por categoría
    category_counts = Categoria.objects.annotate(product_count=Count('productos')).values('nombre', 'product_count')
    category_data = {
        'labels': [cat['nombre'] for cat in category_counts],
        'data': [cat['product_count'] for cat in category_counts]
    }

    # Datos para gráfico de stock por producto (top 10)
    top_stock_products = Product.objects.order_by('-cantidad_stock')[:10]
    stock_data = {
        'labels': [prod.nombre[:20] + '...' if len(prod.nombre) > 20 else prod.nombre for prod in top_stock_products],
        'data': [prod.cantidad_stock for prod in top_stock_products]
    }

    # Contexto específico de la vista de productos
    # Nota: business_name y sidebar_links se añaden automáticamente
    # por el context processor en el_almacen.context_processors.sidebar_context
    return render(request, 'products/list_products.html', {
        'page_title': 'Productos',
        'productos': page_obj,  # Pasar el objeto de página al template
        'categorias': categorias,  # Enviar categorías al template
        'is_admin': is_admin,
        'is_cashier': is_cashier,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'total_value': total_value,
        'category_data': category_data,
        'stock_data': stock_data,
        'search_query': search_query,  # Pasar el término de búsqueda al template
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

    # Calcular métricas para el dashboard
    total_stock = Product.objects.aggregate(total=Sum('cantidad_stock'))['total'] or 0
    low_stock_count = Product.objects.filter(cantidad_stock__lt=10).count()
    total_value = sum(producto.precio_venta * producto.cantidad_stock for producto in Product.objects.all())
    categorias = Categoria.objects.all()

    return render(request, 'products/add_products.html', {
        'page_title': 'Agregar Producto',
        'form': form,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'total_value': total_value,
        'categorias': categorias,
    })

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
    return render(request, 'products/edit_products.html', {
        'page_title': 'Editar Producto',
        'form': form,
        'producto': producto
    })

# -----------------------------------------------------------------------------------------------------------------

def eliminar_producto(request, pk):
    producto = Product.objects.get(pk=pk)

    # Verificar si el usuario es administrador
    if not request.user.is_admin:
        return HttpResponseForbidden("No tienes permiso para eliminar productos.")

    if request.method == 'POST':
        producto.delete()
        return redirect('listar_productos')

    return render(request, 'products/delete_product.html', {
        'page_title': 'Eliminar Producto',
        'producto': producto
    })

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

    # Calcular métricas para el dashboard
    categorias = Categoria.objects.all()
    total_categorias = categorias.count()
    categorias_con_productos = categorias.annotate(product_count=Count('productos')).filter(product_count__gt=0).count()
    categorias_vacias = total_categorias - categorias_con_productos
    total_stock = Product.objects.aggregate(total=Sum('cantidad_stock'))['total'] or 0
    total_value = sum(producto.precio_venta * producto.cantidad_stock for producto in Product.objects.all())

    return render(request, 'products/add_category.html', {
        'page_title': 'Crear Categoría',
        'form': form,
        'total_categorias': total_categorias,
        'categorias_con_productos': categorias_con_productos,
        'categorias_vacias': categorias_vacias,
        'total_stock': total_stock,
        'total_value': total_value,
    })

# -----------------------------------------------------------------------------------------------------------------

# Vista para listar categorías
from django.db.models import Sum, Count, F

# ...

# Vista para listar categorías
def listar_categorias(request):
    # Obtener todas las categorías con cálculos agregados
    categorias = Categoria.objects.annotate(
        product_count=Count('productos'),
        total_stock=Sum('productos__cantidad_stock'),
        total_value=Sum(F('productos__precio_venta') * F('productos__cantidad_stock'))
    ).order_by('nombre')

    # Crear lista de categorías con valores calculados
    categorias_con_valores = []
    for categoria in categorias:
        categorias_con_valores.append({
            'categoria': categoria,
            'total_value': categoria.total_value or 0  # type: ignore
        })

    # Calcular métricas para el dashboard
    total_categorias = categorias.count()
    categorias_con_productos = categorias.filter(product_count__gt=0).count()
    categorias_vacias = total_categorias - categorias_con_productos
    total_stock = Product.objects.aggregate(total=Sum('cantidad_stock'))['total'] or 0
    total_value = sum(producto.precio_venta * producto.cantidad_stock for producto in Product.objects.all())

    # Datos para gráfico de categorías con productos
    category_counts = categorias.values('nombre', 'product_count')
    category_data = {
        'labels': [cat['nombre'] for cat in category_counts],
        'data': [cat['product_count'] for cat in category_counts]
    }

    # Contexto específico de la vista de categorías
    # Nota: business_name y sidebar_links se añaden automáticamente
    # por el context processor en el_almacen.context_processors.sidebar_context
    return render(request, 'products/list_category.html', {
        'page_title': 'Categorías',
        'categorias_con_valores': categorias_con_valores,
        'total_categorias': total_categorias,
        'categorias_con_productos': categorias_con_productos,
        'categorias_vacias': categorias_vacias,
        'total_stock': total_stock,
        'total_value': total_value,
        'category_data': category_data,
    })

# -----------------------------------------------------------------------------------------------------------------

# Vista para editar una categoría
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)

    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre')  # Asumiendo que solo modificas el nombre
        categoria.save()
        messages.success(request, "Categoría actualizada con éxito.")
        return redirect('listar_categorias')

    return render(request, 'products/edit_category.html', {
        'page_title': 'Editar Categoría',
        'categoria': categoria
    })

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
            if producto.qr_code:
                qr_image_path = producto.qr_code.path  # type: ignore
                c.drawImage(qr_image_path, qr_x, qr_y + 10, width=cell_width, height=cell_height - 10)
            else:
                # Si no hay QR code, mostrar un mensaje de error o placeholder
                c.setFont("Helvetica", 8)
                c.drawString(qr_x + 5, qr_y + cell_height/2, "Sin QR")

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
        return render(request, 'products/imprimir_qr.html', {
            'productos': productos,
            'page_title': 'Imprimir QR de Productos'
        })

