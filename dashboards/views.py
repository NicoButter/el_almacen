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

