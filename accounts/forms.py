from django import forms
from .models import Cliente, Telefono, Direccion, Email
from cuentas_corrientes.forms import CuentaCorrienteForm
from cuentas_corrientes.models import CuentaCorriente  # Importar el modelo CuentaCorriente

# --------------------------------------------------------------------------------------------------------------------------

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

# --------------------------------------------------------------------------------------------------------------------------

class TelefonoForm(forms.ModelForm):
    class Meta:
        model = Telefono
        fields = ['numero']

# --------------------------------------------------------------------------------------------------------------------------

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['direccion']

# --------------------------------------------------------------------------------------------------------------------------

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['email']
