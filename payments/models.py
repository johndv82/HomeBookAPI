from django.db import models

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'payment_methods'

    def __str__(self):
        return self.name
