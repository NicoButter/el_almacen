from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from accounts.models import Cliente
from django.db.models import Q
from accounts.forms import ClienteForm, TelefonoForm, DireccionForm, EmailForm
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string



@login_required
def agregar_cliente(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        telefono_form = TelefonoForm(request.POST)
        direccion_form = DireccionForm(request.POST)
        email_form = EmailForm(request.POST)

        if cliente_form.is_valid() and telefono_form.is_valid() and direccion_form.is_valid() and email_form.is_valid():
            # Crear un usuario provisional
            username = get_random_string(8)  # Genera un nombre de usuario único de 8 caracteres
            user = CustomUser.objects.create_user(username=username)

            # Ahora crea el cliente asociado al usuario
            cliente = cliente_form.save(commit=False)
            cliente.user = user  # Asocia el cliente con el usuario recién creado
            cliente.save()

            # Guardar el resto de la información
            telefono = telefono_form.save(commit=False)
            telefono.cliente = cliente  
            telefono.save()

            direccion = direccion_form.save(commit=False)
            direccion.cliente = cliente  
            direccion.save()

            email = email_form.save(commit=False)
            email.cliente = cliente  
            email.save()

            # Agregar un mensaje de éxito
            messages.success(request, 'Cliente agregado correctamente.')
            return redirect('admin_dashboard')
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

# -------------------------------------------------------------------------------------------------------------------

@login_required
def listar_clientes(request):
    query = request.GET.get('query')
    clientes = Cliente.objects.all()
    
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(direcciones__direccion__icontains=query) |
            Q(telefonos__numero__icontains=query) |
            Q(emails__email__icontains=query)
        ).distinct()  # `distinct` evita duplicados si hay múltiples coincidencias en relaciones

    paginator = Paginator(clientes, 10)
    page_number = request.GET.get('page')
    clientes_page = paginator.get_page(page_number)
    
    is_admin = request.user.is_admin  

    return render(request, 'clients/list_clients.html', {
        'clientes': clientes_page,
        'is_admin': is_admin
    })

# --------------------------------------------------------------------------------------------------------------

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clients/edit_client.html', {'form': form, 'cliente': cliente})

# --------------------------------------------------------------------------------------------------------------

@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.delete()  # Elimina el cliente
        messages.success(request, 'Cliente eliminado correctamente.')  # Agregar un mensaje de éxito
        return redirect('listar_clientes')  # Redirige a la lista de clientes
    
    return render(request, 'clients/delete_client.html', {'cliente': cliente})
