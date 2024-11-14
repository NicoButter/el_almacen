from django.db import models
from django.conf import settings
from products.models import Product
from accounts.models import Cliente
from products.models import Product

# ------------------------------------------------------------------------------------------------------------------------------------------

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    productos = models.ManyToManyField(Product, through='DetalleVenta')
    cuenta_corriente = models.ForeignKey('cuentas_corrientes.CuentaCorriente', null=True, blank=True, on_delete=models.SET_NULL)
    
    # Nuevo campo para el tipo de pago
    TIPO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('CUENTA_CORRIENTE', 'Cuenta Corriente')
    ]
    tipo_de_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, null=True, blank=True)

    # Nuevo campo booleano para indicar si la venta es a crédito
    es_fiada = models.BooleanField(default=False)

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre}"

    def realizar_venta_fiada(self):
        """Método para realizar la venta y agregar el total a la cuenta corriente del cliente."""
        if self.cuenta_corriente:
            # Sumamos el total de la venta al saldo de la cuenta corriente
            self.cuenta_corriente.agregar_saldo(self.total)


# ------------------------------------------------------------------------------------------------------------------------------------------

class Ticket(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fiado = models.BooleanField(default=False)

    def __str__(self):
        return f'Ticket {self.id} - {self.date}'

    def save(self, *args, **kwargs):
        if self.fiado and self.cliente:
            cuenta_corriente, created = CuentaCorriente.objects.get_or_create(cliente=self.cliente)
            cuenta_corriente.saldo += self.total
            cuenta_corriente.save()
        super().save(*args, **kwargs)

# ------------------------------------------------------------------------------------------------------------------------------------------

class LineItem(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='line_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.nombre}'

    def save(self, *args, **kwargs):
        # Calcula el subtotal como cantidad * precio del producto
        self.subtotal = self.quantity * self.product.precio_venta
        super().save(*args, **kwargs)

# ------------------------------------------------------------------------------------------------------------------------------------------

# Modelo para registrar los pagos (cuando un cliente paga su saldo fiado)
class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pagos')  # Relacionado con el cliente
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Pago de ${self.monto} - Cliente: {self.cliente.nombre} el {self.fecha.strftime("%d/%m/%Y")}'

# ------------------------------------------------------------------------------------------------------------------------------------------

# Modelo para llevar la cuenta corriente del cliente (saldo deudor)
class CuentaCorriente(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='cuenta_corriente_sales')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'Cuenta Corriente - Cliente: {self.cliente.nombre} - Saldo: ${self.saldo}'

# ------------------------------------------------------------------------------------------------------------------------------------------

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
    
# ------------------------------------------------------------------------------------------------------------------------------------------

def obtener_precio_producto(producto_id):
    try:
        producto = Product.objects.get(id=producto_id)
        return producto.precio_venta  
    except Product.DoesNotExist:
        return None  
    