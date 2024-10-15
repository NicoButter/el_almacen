from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Ticket(models.Model):
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Ticket {self.id} - {self.date}'

class LineItem(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='line_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def save(self, *args, **kwargs):
        # Calcula el subtotal como cantidad * precio del producto
        self.subtotal = self.quantity * self.product.price
        super().save(*args, **kwargs)
