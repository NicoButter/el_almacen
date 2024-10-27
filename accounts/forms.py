from django import forms
from .models import Cliente, Telefono, Direccion, Email

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre']

class TelefonoForm(forms.ModelForm):
    class Meta:
        model = Telefono
        fields = ['numero']

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['direccion']

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['email']
