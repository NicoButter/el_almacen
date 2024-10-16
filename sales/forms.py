from django import forms
from .models import Ticket, LineItem
from products.models import Product

class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ['product', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(stock__gt=0)  # Mostrar solo productos con stock

class NewSaleForm(forms.ModelForm):
    items = forms.CharField(widget=forms.HiddenInput())  # Campo para almacenar los productos seleccionados

    class Meta:
        model = Ticket
        fields = []  # Solo usamos este formulario para crear el Ticket

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['items'] = forms.Field(required=False)
