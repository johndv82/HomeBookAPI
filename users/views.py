from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Client, Address
from .serializers import ClientSerializer, AddressSerializer


class ClientMeView(generics.RetrieveAPIView):
    """
    GET /users/client/me/
        Devuelve el perfil del cliente autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientSerializer

    def get_object(self):
        return Client.objects.get(user=self.request.user)


class AddressListView(generics.ListCreateAPIView):
    """
    GET /users/addresses/
        Devuelve todas las direcciones
    POST /users/addresses/
        Crea un nueva dirección
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(client__user=self.request.user)

    def perform_create(self, serializer):
        client = Client.objects.get(user=self.request.user)
        serializer.save(client=client)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /users/addresses/<id>/
    PATCH /users/addresses/<id>/
    DELETE /users/addresses/<id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(client__user=self.request.user)
