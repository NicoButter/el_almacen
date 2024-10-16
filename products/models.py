from django.db import models
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils.text import slugify  # Asegúrate de importar slugify

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

        # Guarda la imagen en un archivo
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        # Usa el nombre del producto para crear un nombre de archivo único
        filename = slugify(self.nombre)  # Convierte el nombre a un formato seguro para archivos
        return ContentFile(buffer.getvalue(), name=f'{filename}_qr.png')  # Guarda con el nombre del producto
