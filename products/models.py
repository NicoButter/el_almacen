from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils.text import slugify  # Asegúrate de importar slugify

# Opciones para la unidad de medida
UNIDAD_MEDIDA_CHOICES = [
    ('kg', 'Kilogramo'),
    ('unidad', 'Unidad')
]

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Product(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)  # Costo del producto
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))  # Porcentaje de ganancia
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=Decimal('0.00'))  # Precio de venta (no editable directamente)
    
    cantidad_stock = models.DecimalField(max_digits=10, decimal_places=2)  # Usamos DecimalField para manejar decimales en kg
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_MEDIDA_CHOICES, default='kg')  # Unidad de medida (kg o unidad)
    
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    se_vende_fraccionado = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, related_name='productos', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.unidad_medida = 'kg' if self.se_vende_fraccionado else 'unidad'
        self.precio_venta = self.calcular_precio_venta()
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.qr_code = self.generar_qr_code()
            super().save(update_fields=['qr_code'])

    def calcular_precio_venta(self):
        """Calcula el precio de venta basado en el costo y el porcentaje de ganancia."""
        costo = Decimal(self.costo or 0)
        porcentaje = Decimal(self.porcentaje_ganancia or 0)
        precio = costo * (Decimal('1') + (porcentaje / Decimal('100')))
        return precio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def clean(self):
        super().clean()
        errores = {}
        for campo in ('costo', 'porcentaje_ganancia', 'cantidad_stock'):
            valor = getattr(self, campo)
            if valor is not None and valor < 0:
                errores[campo] = 'El valor no puede ser negativo.'
        if errores:
            raise ValidationError(errores)

    def generar_qr_code(self):
        """Genera un QR con el ID del producto y lo guarda usando la Storage API de Django."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(self.id))
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"{slugify(self.nombre)}_qr.png"
        
        # Usamos ContentFile para que Django maneje el guardado a través del campo qr_code
        file_content = ContentFile(buffer.getvalue(), name=filename)
        return file_content

    def actualizar_stock(self, cantidad_vendida):
        """Descuenta del stock la cantidad vendida, expresada en la unidad de stock del producto."""
        try:
            cantidad = Decimal(str(cantidad_vendida))
        except (InvalidOperation, TypeError) as exc:
            raise ValueError('La cantidad vendida debe ser un número válido.') from exc

        if cantidad <= 0:
            raise ValueError('La cantidad vendida debe ser mayor a cero.')

        nuevo_stock = self.cantidad_stock - cantidad
        if nuevo_stock < 0:
            raise ValueError('No hay stock suficiente para completar la operación.')

        self.cantidad_stock = nuevo_stock
        self.save(update_fields=['cantidad_stock', 'precio_venta', 'unidad_medida'])
