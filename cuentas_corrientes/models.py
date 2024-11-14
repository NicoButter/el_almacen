from django.db import models
from accounts.models import Cliente

class CuentaCorriente(models.Model):
    cliente = models.OneToOneField('accounts.Cliente', on_delete=models.CASCADE, related_name='cuenta_corriente_cc')
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_apertura = models.DateField()

    def __str__(self):
        return f"Cuenta Corriente de {self.cliente.nombre}"
