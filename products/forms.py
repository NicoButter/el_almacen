from django import forms
from .models import Product, Categoria

class ProductForm(forms.ModelForm):
    SE_VENDE_FRACCIONADO_CHOICES = [
        (True, 'Sí'),
        (False, 'No'),
    ]

    se_vende_fraccionado = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Product
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_stock', 'imagen', 'se_vende_fraccionado', 'categoria']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']