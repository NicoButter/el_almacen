from django import forms
from .models import CuentaCorriente

class CuentaCorrienteForm(forms.ModelForm):
    class Meta:
        model = CuentaCorriente
        fields = ['cliente', 'saldo'] 
