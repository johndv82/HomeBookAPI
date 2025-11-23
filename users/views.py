from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Client, Address
from .serializers import (
    ClientSerializer,
    AddressSerializer,
)


class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Perfil del cliente (solo lectura).
    GET /clients/me/
    """
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        instance = Client.objects.get(user=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    """
    CRUD de direcciones del cliente autenticado.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(client__user=self.request.user)

    def perform_create(self, serializer):
        client = Client.objects.get(user=self.request.user)
        serializer.save(client=client)
