from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from .models import Product, Categoria
from .forms import ProductForm, CategoriaForm

# -----------------------------------------------------------------------------------------------------------------

def listar_productos(request):
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = Product.objects.filter(categoria_id=categoria_id)
    else:
        productos = Product.objects.all()

    categorias = Categoria.objects.all()  # Obtener todas las categorías

    is_admin = request.user.is_admin
    is_cashier = request.user.is_cashier

    return render(request, 'products/list_products.html', {
        'productos': productos,
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

# Vista para eliminar una categoría
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