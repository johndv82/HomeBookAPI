from django.db import models
from orders.models import Order

class Shipping(models.Model):
    #Datos de envío asociados a la orden
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'shipping'

    def __str__(self):
        return f"Shipping for Order #{self.order.id}"