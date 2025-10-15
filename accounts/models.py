from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_cashier = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def get_dashboard_url(self):
        """Return the named URL to redirect the user to after login depending on role."""
        if self.is_admin:
            return 'dashboard:admin_dashboard'
        if self.is_cashier:
            return 'dashboard:cashier_dashboard'
        # default to user dashboard (clients handled separately)
        return 'dashboard:user_dashboard'

class Cliente(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cliente_profile')
    nombre = models.CharField(max_length=100)

    if TYPE_CHECKING:
        # Type hint for Pylance to recognize the email property through user relationship
        @property
        def email(self) -> str:
            return self.user.email

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
