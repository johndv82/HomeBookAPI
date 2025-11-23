from rest_framework import serializers
from .models import Shipping


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = [
            "id",
            "order",
            "tracking_number",
            "carrier",
            "shipped_at",
            "delivered_at",
            "shipping_cost",
        ]
        read_only_fields = ["order"]
