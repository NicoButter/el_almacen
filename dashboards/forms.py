from django import forms
from products.models import Product, Categoria

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nombre', 'descripcion', 'costo', 'porcentaje_ganancia', 'cantidad_stock', 'imagen', 'se_vende_fraccionado', 'categoria']
