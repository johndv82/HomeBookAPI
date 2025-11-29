from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    CheckoutSerializer, OrderSerializer
)
from users.models import Client, Address
from books.models import Books
from payments.models import PaymentMethod



# Obtener / crear carrito
def get_or_create_cart(client):
    cart, created = Cart.objects.get_or_create(client=client, is_active=True)
    return cart

# Listar carrito
class CartDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        client, _ = Client.objects.get_or_create(user=self.request.user)
        return get_or_create_cart(client)


# Agregar al carrito
class AddToCartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book = Books.objects.get(id=serializer.validated_data["book_id"])
        quantity = serializer.validated_data["quantity"]

        client, _ = Client.objects.get_or_create(user=request.user)
        cart = get_or_create_cart(client)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
        cart_item.quantity += quantity
        cart_item.save()

        return Response(CartSerializer(cart).data)


# Eliminar item del carrito
class RemoveCartItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__client__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Item no encontrado."}, status=404)

        cart = item.cart
        item.delete()
        return Response(CartSerializer(cart).data)


# Volcar datos del carrito en una Orden de Venta
class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = serializer.validated_data["client"]
        address = Address.objects.get(id=serializer.validated_data["address_id"])
        payment = PaymentMethod.objects.get(id=serializer.validated_data["payment_method_id"])

        cart = get_or_create_cart(client)

        if cart.items.count() == 0:
            return Response({"error": "El carrito está vacío."}, status=400)

        # Crear orden
        order = Order.objects.create(
            client=client,
            address=address,
            payment_method=payment,
            total_amount=cart.total(),
        )

        # Crear items de la orden
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )

        # Desactivar carrito
        cart.is_active = False
        cart.save()

        return Response(OrderSerializer(order).data, status=201)


# Listar órdenes
class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        client, _ = Client.objects.get_or_create(user=self.request.user)
        return client.orders.all().order_by("-created_at")


# Listar Detalle de la Orden
class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        client, _ = Client.objects.get_or_create(user=self.request.user)
        return client.orders.all()
