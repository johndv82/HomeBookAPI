from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import PaymentMethod
from .serializers import PaymentMethodSerializer

# LISTAR / CREAR MÉTODOS DE PAGO
class PaymentMethodListView(generics.ListCreateAPIView):
    queryset = PaymentMethod.objects.all().order_by("name")
    serializer_class = PaymentMethodSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]


# DETALLE / UPDATE / DELETE
class PaymentMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]
