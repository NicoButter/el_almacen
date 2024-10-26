from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_cashier = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Cliente(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cliente_profile')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Telefono(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='telefonos')
    numero = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.direccion} - {self.cliente.nombre}"

class Email(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField(validators=[EmailValidator()], unique=True)

    def __str__(self):
        return f"{self.email} - {self.cliente.nombre}"
