from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from accounts.models import Cliente
from django.db.models import Q
from accounts.forms import ClienteForm, TelefonoForm, DireccionForm, EmailForm
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from cuentas_corrientes.forms import CuentaCorrienteForm
import logging
from django.contrib.auth.decorators import login_required


#----------------------------------------------------------------------------------------------------------------------------

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
    
    # Usamos `prefetch_related` para optimizar la consulta, aunque ahora solo hay una cuenta corriente por cliente
    clientes = Cliente.objects.prefetch_related('direcciones', 'telefonos', 'emails', 'cuenta_corriente_cc').all()

    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(direcciones__direccion__icontains=query) |
            Q(telefonos__numero__icontains=query) |
            Q(emails__email__icontains=query)
        ).distinct()

    paginator = Paginator(clientes, 10)
    page_number = request.GET.get('page')
    clientes_page = paginator.get_page(page_number)
    
    is_admin = request.user.is_admin  

    return render(request, 'clients/list_clients.html', {
        'clientes': clientes_page,
        'is_admin': is_admin
    })

# --------------------------------------------------------------------------------------------------------------

# views.py

import logging
from cuentas_corrientes.forms import CuentaCorrienteForm

# Crea un logger
logger = logging.getLogger(__name__)

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    # Verificar si el cliente tiene una cuenta corriente asociada
    cuenta_corriente = cliente.cuenta_corriente_cc if hasattr(cliente, 'cuenta_corriente_cc') else None
    
    logger.debug(f"Cliente encontrado: {cliente}")
    logger.debug(f"Cuenta corriente asociada: {cuenta_corriente}")

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)

        # Si el cliente tiene una cuenta corriente, pasamos la instancia de cuenta corriente al formulario
        if cuenta_corriente:
            cuenta_corriente_form = CuentaCorrienteForm(request.POST, instance=cuenta_corriente)
        else:
            cuenta_corriente_form = CuentaCorrienteForm(request.POST)

        logger.debug("Formulario de cliente procesado")
        logger.debug(f"Formulario de cuenta corriente: {cuenta_corriente_form}")

        if form.is_valid() and cuenta_corriente_form.is_valid():
            form.save()  # Guardamos el cliente
            logger.debug("Formulario de cliente guardado exitosamente")

            # Si la cuenta corriente existe o es válida, guarda los cambios
            if cuenta_corriente_form.has_changed():
                cuenta_corriente_form.save()
                logger.debug("Formulario de cuenta corriente guardado exitosamente")

            return redirect('listar_clientes')
        else:
            logger.error(f"Formulario no válido: {form.errors}")
            logger.error(f"Formulario de cuenta corriente no válido: {cuenta_corriente_form.errors}")
    else:
        form = ClienteForm(instance=cliente)

        if cuenta_corriente:
            cuenta_corriente_form = CuentaCorrienteForm(instance=cuenta_corriente)
        else:
            cuenta_corriente_form = CuentaCorrienteForm()

    return render(request, 'clients/edit_client.html', {
        'form': form,
        'cuenta_corriente_form': cuenta_corriente_form,  
        'cliente': cliente,
    })


# --------------------------------------------------------------------------------------------------------------

@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.delete()  # Elimina el cliente
        messages.success(request, 'Cliente eliminado correctamente.')  # Agregar un mensaje de éxito
        return redirect('listar_clientes')  # Redirige a la lista de clientes
    
    return render(request, 'clients/delete_client.html', {'cliente': cliente})
