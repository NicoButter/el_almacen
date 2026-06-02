from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import models

class CuentaCorriente(models.Model):
    cliente = models.OneToOneField('accounts.Cliente', on_delete=models.CASCADE, related_name='cuenta_corriente_cc')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Establecer un valor predeterminado
    fecha_apertura = models.DateField(default=date.today)

    @staticmethod
    def _normalizar_monto(monto):
        try:
            monto_decimal = Decimal(str(monto))
        except (InvalidOperation, TypeError) as exc:
            raise ValueError('El monto debe ser un número válido.') from exc

        if monto_decimal <= 0:
            raise ValueError('El monto debe ser mayor a cero.')
        return monto_decimal.quantize(Decimal('0.01'))

    def agregar_saldo(self, monto):
        """Método para agregar un monto al saldo de la cuenta corriente."""
        self.saldo += self._normalizar_monto(monto)
        self.save(update_fields=['saldo'])

    def registrar_pago(self, monto):
        """Descuenta un pago del saldo pendiente."""
        monto_decimal = self._normalizar_monto(monto)
        if monto_decimal > self.saldo:
            raise ValueError('El monto no puede ser mayor al saldo disponible.')
        self.saldo -= monto_decimal
        self.save(update_fields=['saldo'])

    def __str__(self):
        return f"Cuenta Corriente de {self.cliente.nombre} - Saldo: {self.saldo} "
