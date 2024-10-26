from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Cliente
from .forms import ClienteForm  
from django.core.paginator import Paginator
from django.db.models import Q


@login_required
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_clients')
    else:
        form = ClienteForm()
    return render(request, 'clients/add_client.html', {'form': form})

@login_required
def listar_clientes(request):
    query = request.GET.get('query')
    clientes = Cliente.objects.all()
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(direccion__icontains=query) |
            Q(telefono__icontains=query) |
            Q(email__icontains=query)
        )
    paginator = Paginator(clientes, 10)  # 10 clientes por página
    page_number = request.GET.get('page')
    clientes_page = paginator.get_page(page_number)
    return render(request, 'clients/list_clients.html', {'clientes': clientes_page})

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('list_clients')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clients/edit_client.html', {'form': form, 'cliente': cliente})


@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.delete()  # Elimina el cliente
        return redirect('list_clients')  # Redirige a la lista de clientes
    
    return render(request, 'clients/eliminar_cliente.html', {'cliente': cliente})