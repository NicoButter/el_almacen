from django.shortcuts import render, redirect, get_object_or_404
from .models import CuentaCorriente
from .forms import CuentaCorrienteForm
from django.contrib import messages


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

