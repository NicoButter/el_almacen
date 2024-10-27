from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Cliente
from accounts.forms import ClienteForm, TelefonoForm, DireccionForm, EmailForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages



@login_required
def agregar_cliente(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        telefono_form = TelefonoForm(request.POST)
        direccion_form = DireccionForm(request.POST)
        email_form = EmailForm(request.POST)

        if cliente_form.is_valid() and telefono_form.is_valid() and direccion_form.is_valid() and email_form.is_valid():
            cliente = cliente_form.save()
            telefono = telefono_form.save(commit=False)
            telefono.cliente = cliente  # Asocia el teléfono al cliente
            telefono.save()
            direccion = direccion_form.save(commit=False)
            direccion.cliente = cliente  # Asocia la dirección al cliente
            direccion.save()
            email = email_form.save(commit=False)
            email.cliente = cliente  # Asocia el email al cliente
            email.save()

            # Agregar un mensaje de éxito
            messages.success(request, 'Cliente agregado correctamente.')
            return redirect('admin_dashboard')  # Redirigir a donde quieras (a tu panel de administración)
    else:
        cliente_form = ClienteForm()
        telefono_form = TelefonoForm()
        direccion_form = DireccionForm()
        email_form = EmailForm()

    context = {
        'cliente_form': cliente_form,
        'telefono_form': telefono_form,
        'direccion_form': direccion_form,
        'email_form': email_form,
    }
    return render(request, 'clients/add_client.html', context)

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