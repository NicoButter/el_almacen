from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .forms import ProductForm 
from django.contrib.auth.decorators import login_required

@login_required
def admin_dashboard(request):
    # Si se envía un formulario POST, procesamos la adición de productos
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()

    # Listamos todos los productos
    productos = Product.objects.all()

    return render(request, 'dashboards/admin_dashboard.html', {
        'form': form,
        'productos': productos
    })

@login_required
def cashier_dashboard(request):
    return render(request, 'dashboards/cashier_dashboard.html')

@login_required
def user_dashboard(request):
    return render(request, 'dashboards/user_dashboard.html')


# @login_required
# def editar_producto(request, pk):
#     # Obtener el producto por su primary key (pk), si no existe, devolver 404
#     producto = get_object_or_404(Product, pk=pk)

#     if request.method == 'POST':
#         # Cargar el formulario con los datos del POST y los archivos (si los hay) y usar el producto existente
#         form = ProductForm(request.POST, request.FILES, instance=producto)
#         if form.is_valid():
#             form.save()
#             return redirect('admin_dashboard')  # O redirigir a la lista de productos si lo prefieres
#     else:
#         # Cargar el formulario con los datos del producto existente
#         form = ProductForm(instance=producto)

#     return render(request, 'productos/editar_producto.html', {
#         'form': form,
#         'producto': producto
#     })

# @login_required
# def eliminar_producto(request, pk):
#     # Obtener el producto por su primary key (pk), si no existe, devolver 404
#     producto = get_object_or_404(Product, pk=pk)

#     if request.method == 'POST':
#         # Eliminar el producto si se recibe un POST
#         producto.delete()
#         return redirect('admin_dashboard')  # O redirigir a la lista de productos si lo prefieres

#     # Mostrar la confirmación de eliminación
#     return render(request, 'productos/eliminar_producto.html', {
#         'producto': producto
#     })

