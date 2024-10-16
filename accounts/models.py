from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_cashier = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    
class Cliente(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cliente_profile')
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre