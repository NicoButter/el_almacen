from django.shortcuts import render, redirect, get_object_or_404
from .models import CuentaCorriente
from .forms import CuentaCorrienteForm
from django.contrib import messages
from accounts.models import Cliente
from django.contrib.auth.decorators import login_required

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

def asignar_cuenta_corriente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)  # Obtén el cliente por ID

    if request.method == 'POST':
        form = CuentaCorrienteForm(request.POST)  # Crea un formulario con los datos enviados
        if form.is_valid():
            cuenta_corriente = form.save(commit=False)  # No guardes aún
            cuenta_corriente.cliente = cliente  # Asigna el cliente a la cuenta corriente
            cuenta_corriente.saldo = 0  # Establece el saldo inicial a 0
            cuenta_corriente.save()  # Guarda la cuenta corriente
            return redirect('listar_clientes')  # Redirige a la lista de clientes

    else:
        form = CuentaCorrienteForm()  # Si no es POST, crea un formulario vacío

    return render(request, 'cuentas_corrientes/asignar_cuenta_corriente.html', {'form': form, 'cliente': cliente})