from django.db import models
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils.text import slugify  # Asegúrate de importar slugify
import os
from pathlib import Path
from django.conf import settings

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
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Porcentaje de ganancia
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.00)  # Precio de venta (no editable directamente)
    
    cantidad_stock = models.DecimalField(max_digits=10, decimal_places=2)  # Usamos DecimalField para manejar decimales en kg
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_MEDIDA_CHOICES, default='kg')  # Unidad de medida (kg o unidad)
    
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    se_vende_fraccionado = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.precio_venta = self.calcular_precio_venta()
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.qr_code = self.generar_qr_code()
            super().save(update_fields=['qr_code'])

    def calcular_precio_venta(self):
        """Calcula el precio de venta basado en el costo y el porcentaje de ganancia."""
        return round(self.costo * (1 + (self.porcentaje_ganancia / 100)), 2)

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
        self.cantidad_stock -= cantidad_vendida
        self.save()
