from django.shortcuts import render, redirect, get_object_or_404
from .models import CuentaCorriente
from .forms import CuentaCorrienteForm
from django.contrib import messages
from accounts.models import Cliente
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


# -------------------------------------------------------------------------------------------------------------------

@login_required
def gestion_cuentas_corrientes(request):
    clientes = Cliente.objects.all()  # Obtener todos los clientes
    paginator = Paginator(clientes, 10)  # Mostrar 10 clientes por página
    page_number = request.GET.get('page')  # Obtener el número de página de la URL
    page_obj = paginator.get_page(page_number)  # Obtener los clientes para la página actual

    clientes_con_estado = []
    for cliente in page_obj:
        cuenta_corriente = CuentaCorriente.objects.filter(cliente=cliente).first()
        clientes_con_estado.append({
            'cliente': cliente,
            'tiene_cuenta': cuenta_corriente is not None,
            'saldo': cuenta_corriente.saldo if cuenta_corriente else None,
        })

    return render(request, 'cuentas_corrientes/gestion_cuentas_corrientes.html', {'clientes_con_estado': clientes_con_estado, 'page_obj': page_obj})

# -------------------------------------------------------------------------------------------------------------------

def crear_cuenta_corriente(request):
    if request.method == 'POST':
        form = CuentaCorrienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_cuentas_corrientes')  # Asegúrate de definir esta URL
    else:
        form = CuentaCorrienteForm()
    return render(request, 'cuentas_corrientes/crear_cuenta.html', {'form': form})

# -------------------------------------------------------------------------------------------------------------------

@login_required
def editar_cuenta_corriente(request, pk):
    cuenta_corriente = get_object_or_404(CuentaCorriente, pk=pk)

    if request.method == 'POST':
        form = CuentaCorrienteForm(request.POST, instance=cuenta_corriente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta corriente actualizada correctamente.')
            return redirect('listar_clientes')  # O la página que prefieras
    else:
        form = CuentaCorrienteForm(instance=cuenta_corriente)

    return render(request, 'cuentas_corrientes/edit_cuenta.html', {'form': form, 'cuenta_corriente': cuenta_corriente})

# -------------------------------------------------------------------------------------------------------------------

def agregar_saldo(request, cuenta_id):
    cuenta = get_object_or_404(CuentaCorriente, id=cuenta_id)
    if request.method == 'POST':
        monto = float(request.POST.get('monto'))
        if monto > 0:
            cuenta.agregar_saldo(monto)
            messages.success(request, 'Saldo agregado correctamente.')
            return redirect('detalle_cuenta_corriente', cuenta_id=cuenta.id)  # Asegúrate de definir esta URL
        else:
            messages.error(request, 'El monto debe ser positivo.')
    return render(request, 'cuentas_corrientes/agregar_saldo.html', {'cuenta': cuenta})

# --------------------------------------------------------------------------------------------------------------------

def pagar_cuenta(request, cuenta_id):
    cuenta = get_object_or_404(CuentaCorriente, id=cuenta_id)
    if request.method == 'POST':
        monto = float(request.POST.get('monto'))
        try:
            cuenta.pagar(monto)
            messages.success(request, 'Pago registrado correctamente.')
            return redirect('detalle_cuenta_corriente', cuenta_id=cuenta.id)  # Asegúrate de definir esta URL
        except ValueError as e:
            messages.error(request, str(e))
    return render(request, 'cuentas_corrientes/pagar_cuenta.html', {'cuenta': cuenta})

# --------------------------------------------------------------------------------------------------------------------

@login_required
def asignar_cuenta_corriente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    # Verifica si el cliente ya tiene una cuenta corriente
    if hasattr(cliente, 'cuentacorriente'):
        messages.warning(request, f'{cliente.nombre} ya tiene una cuenta corriente asignada.')
        return redirect('listar_clientes')

    if request.method == 'POST':
        form = CuentaCorrienteForm(request.POST)
        if form.is_valid():
            cuenta_corriente = form.save(commit=False)
            cuenta_corriente.cliente = cliente
            cuenta_corriente.saldo = 0  # Saldo inicial
            cuenta_corriente.save()
            messages.success(request, f'Cuenta corriente asignada a {cliente.nombre} correctamente.')
            return redirect('listar_clientes')
    else:
        form = CuentaCorrienteForm()

    return render(request, 'cuentas_corrientes/asignar_cuenta_corriente.html', {'form': form, 'cliente': cliente})

# --------------------------------------------------------------------------------------------------------------------

@login_required
def eliminar_cuenta_corriente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    cuenta_corriente = getattr(cliente, 'cuentacorriente', None)  # Asume relación OneToOneField
    if cuenta_corriente:
        cuenta_corriente.delete()
        messages.success(request, f'Cuenta corriente de {cliente.nombre} eliminada correctamente.')
    else:
        messages.error(request, f'{cliente.nombre} no tiene una cuenta corriente asignada.')
    return redirect('listar_clientes')  # Redirige a la lista de clientes
