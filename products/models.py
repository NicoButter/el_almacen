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

# class Product(models.Model):
#     nombre = models.CharField(max_length=100)
#     descripcion = models.TextField()
#     costo = models.DecimalField(max_digits=10, decimal_places=2)  # Costo del producto
#     porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Porcentaje de ganancia
#     precio_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.00)  # Precio de venta (no editable directamente)
#     cantidad_stock = models.PositiveIntegerField()
#     imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
#     se_vende_fraccionado = models.BooleanField(default=False)
#     qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
#     categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos', null=True, blank=True)

#     def save(self, *args, **kwargs):
#         self.precio_venta = self.calcular_precio_venta()  # Calcular precio de venta antes de guardar
#         super().save(*args, **kwargs)  # Guardamos primero el producto para asegurarnos de que tiene un ID
#         if not self.qr_code:
#             self.qr_code = self.generar_qr_code()  # Generamos el QR con el ID
#             super().save(update_fields=['qr_code', 'precio_venta'])  # Volvemos a guardar para actualizar el campo del QR y precio de venta

#     def calcular_precio_venta(self):
#         """Calcula el precio de venta basado en el costo y el porcentaje de ganancia."""
#         return round(self.costo * (1 + (self.porcentaje_ganancia / 100)), 2)

#     def generar_qr_code(self):
#         # Usar el ID del producto para el código QR
#         product_id = self.id

#         # Generar el código QR con el ID del producto
#         qr = qrcode.QRCode(version=1, box_size=10, border=5)
#         qr.add_data(product_id)  # Solo el ID
#         qr.make(fit=True)

#         img = qr.make_image(fill='black', back_color='white')

#         # Crear la ruta de guardado en media/qr_codes/
#         qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
#         Path(qr_code_path).mkdir(parents=True, exist_ok=True)

#         # Usar el nombre del producto para crear un nombre de archivo único
#         filename = slugify(self.nombre)
#         file_path = os.path.join(qr_code_path, f'{filename}_qr.png')

#         # Guardar la imagen en un archivo en el sistema de archivos
#         with open(file_path, 'wb') as f:
#             buffer = BytesIO()
#             img.save(buffer, format='PNG')
#             f.write(buffer.getvalue())

#         # Devolver el nombre del archivo para almacenarlo en la base de datos
#         return f'qr_codes/{filename}_qr.png'


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
        self.precio_venta = self.calcular_precio_venta()  # Calcular precio de venta antes de guardar
        super().save(*args, **kwargs)  # Guardamos primero el producto para asegurarnos de que tiene un ID
        if not self.qr_code:
            self.qr_code = self.generar_qr_code()  # Generamos el QR con el ID
            super().save(update_fields=['qr_code', 'precio_venta'])  # Volvemos a guardar para actualizar el campo del QR y precio de venta

    def calcular_precio_venta(self):
        """Calcula el precio de venta basado en el costo y el porcentaje de ganancia."""
        return round(self.costo * (1 + (self.porcentaje_ganancia / 100)), 2)

    def generar_qr_code(self):
        # Usar el ID del producto para el código QR
        product_id = self.id

        # Generar el código QR con el ID del producto
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(product_id)  # Solo el ID
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Crear la ruta de guardado en media/qr_codes/
        qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        Path(qr_code_path).mkdir(parents=True, exist_ok=True)

        # Usar el nombre del producto para crear un nombre de archivo único
        filename = slugify(self.nombre)
        file_path = os.path.join(qr_code_path, f'{filename}_qr.png')

        # Guardar la imagen en un archivo en el sistema de archivos
        with open(file_path, 'wb') as f:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            f.write(buffer.getvalue())

        # Devolver el nombre del archivo para almacenarlo en la base de datos
        return f'qr_codes/{filename}_qr.png'

    def actualizar_stock(self, cantidad_vendida):
        """Actualiza el stock del producto según la cantidad vendida."""
        if self.unidad_medida == 'kg':
            # Si la unidad de medida es kg, restamos la cantidad en kilogramos
            self.cantidad_stock -= cantidad_vendida
        elif self.unidad_medida == 'unidad':
            # Si la unidad de medida es 'unidad', restamos una unidad
            self.cantidad_stock -= 1
        self.save()