from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    SE_VENDE_FRACCIONADO_CHOICES = [
        (True, 'Sí'),
        (False, 'No'),
    ]

    # se_vende_fraccionado = forms.ChoiceField(
    #     choices=SE_VENDE_FRACCIONADO_CHOICES,
    #     widget=forms.Select(attrs={'class': 'form-control'})
    # )

    se_vende_fraccionado = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Product
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_stock', 'imagen', 'se_vende_fraccionado']
