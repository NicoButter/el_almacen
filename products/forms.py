from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_stock', 'imagen', 'se_vende_fraccionado'] 

