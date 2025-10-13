from django import forms
from .models import CuentaCorriente

class CuentaCorrienteForm(forms.ModelForm):
    class Meta:
        model = CuentaCorriente
        fields = '__all__'

    # Puedes hacer que los campos no sean obligatorios:
    saldo = forms.DecimalField(required=False)  # Ejemplo: hacer que el saldo no sea obligatorio
    fecha_apertura = forms.DateField(required=False)  # Hacer que la fecha de apertura no sea obligatoria