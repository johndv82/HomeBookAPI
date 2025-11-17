from django.db import models

# Create your models here.

class PaymentMethod(models.Model):
    """Métodos de pago disponibles"""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'payment_methods'

    def __str__(self):
        return self.name
