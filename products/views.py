from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm

def listar_productos(request):
    productos = Product.objects.all()
    # Retornar los productos al template
    return render(request, 'products/list_products.html', {'productos': productos})

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Asegurarse de incluir request.FILES
        if form.is_valid():
            producto = form.save(commit=False)  # No guardes el producto aún
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']  # Guarda la imagen en el campo de imagen
            producto.save()  # Ahora guarda el producto junto con la imagen
            return redirect('listar_productos')
    else:
        form = ProductForm()
    return render(request, 'products/add_products.html', {'form': form})


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

def eliminar_producto(request, pk):
    producto = Product.objects.get(pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('listar_productos')
    return render(request, 'products/delete_product.html', {'producto': producto})
