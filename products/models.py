from django.db import models
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils.text import slugify  # Asegúrate de importar slugify
import os
from pathlib import Path
from django.conf import settings


class Product(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    se_vende_fraccionado = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guardamos primero el producto para asegurarnos de que tiene un ID
        if not self.qr_code:
            self.qr_code = self.generar_qr_code()  # Generamos el QR con el ID
            super().save(update_fields=['qr_code'])  # Volvemos a guardar para actualizar el campo del QR

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
