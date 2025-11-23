from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404

from .models import Shipping
from .serializers import ShippingSerializer


class ShippingListView(generics.ListAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Shipping de órdenes que pertenecen al usuario
        return Shipping.objects.filter(order__user=self.request.user)


class ShippingDetailView(generics.RetrieveAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Shipping.objects.filter(order__user=self.request.user)
