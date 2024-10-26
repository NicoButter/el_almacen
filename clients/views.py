from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Cliente
from .forms import ClienteForm  

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
    clientes = Cliente.objects.all()
    return render(request, 'clients/list_clients.html', {'clientes': clientes})

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