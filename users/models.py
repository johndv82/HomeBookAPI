from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """Usuario base para autenticación con Djoser"""
    email = models.EmailField(unique=True)
    is_client = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class Client(models.Model):
    """Perfil extendido del cliente"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'clients'

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Address(models.Model):
    """Direcciones de envío del cliente"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Perú")
    phone = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'addresses'

    def __str__(self):
        return f"{self.full_name} - {self.city}"