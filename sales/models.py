from django.db import models
from django.conf import settings
from products.models import Product
from accounts.models import Cliente  # Importa el modelo Cliente desde accounts

class Ticket(models.Model):
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')  # Relaciona al ticket con un cliente
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fiado = models.BooleanField(default=False)  # Añade el campo para identificar si la venta fue fiada o no

    def __str__(self):
        return f'Ticket {self.id} - {self.date}'

    def save(self, *args, **kwargs):
        # Si la venta fue fiada, actualiza el saldo de la cuenta corriente del cliente
        if self.fiado and self.cliente:
            cuenta_corriente, created = CuentaCorriente.objects.get_or_create(cliente=self.cliente)
            cuenta_corriente.saldo += self.total
            cuenta_corriente.save()
        super().save(*args, **kwargs)

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

# Modelo para registrar los pagos (cuando un cliente paga su saldo fiado)
class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pagos')  # Relacionado con el cliente
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Pago de ${self.monto} - Cliente: {self.cliente.nombre} el {self.fecha.strftime("%d/%m/%Y")}'

# # Modelo para llevar la cuenta corriente del cliente (saldo deudor)
# class CuentaCorriente(models.Model):
#     cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='cuenta_corriente')
#     saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

#     def __str__(self):
#         return f'Cuenta Corriente - Cliente: {self.cliente.nombre} - Saldo: ${self.saldo}'
