from django.db import models
from accounts.models import Cliente

class CuentaCorriente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cuentas_corrientes')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Este campo representa la deuda total
    fecha_apertura = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Cuenta de {self.cliente.nombre} - Saldo: {self.saldo}'

    def agregar_saldo(self, monto):
        self.saldo += monto
        self.save()

    def pagar(self, monto):
        if monto <= self.saldo:
            self.saldo -= monto
            self.save()
        else:
            raise ValueError("El pago excede el saldo de la cuenta.")
