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
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = self.generar_qr_code()
        super().save(*args, **kwargs)

    def generar_qr_code(self):
        # Usa solo el ID del producto para el código QR
        product_id = self.id

        # Genera el código QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(product_id)  # Solo el ID
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Crea la ruta de guardado en media/qr_codes/
        qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        
        # Asegúrate de que la carpeta qr_codes existe
        Path(qr_code_path).mkdir(parents=True, exist_ok=True)

        # Usa el nombre del producto para crear un nombre de archivo único
        filename = slugify(self.nombre)  # Convierte el nombre del producto en un slug seguro para archivos
        file_path = os.path.join(qr_code_path, f'{filename}_qr.png')

        # Guarda la imagen en un archivo en el sistema de archivos
        with open(file_path, 'wb') as f:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            f.write(buffer.getvalue())

        # Devuelve el nombre del archivo para su almacenamiento en la base de datos o donde lo necesites
        return f'qr_codes/{filename}_qr.png'
