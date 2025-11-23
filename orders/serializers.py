from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from books.models import Books
from users.models import Client, Address
from payments.models import PaymentMethod

class CartItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_price = serializers.DecimalField(
        source="book.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "book", "book_title", "book_price", "quantity", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "client", "items", "total", "created_at", "updated_at"]
        read_only_fields = ["client"]

    def get_total(self, obj):
        return obj.total()


class AddToCartSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_book_id(self, value):
        if not Books.objects.filter(id=value).exists():
            raise serializers.ValidationError("El libro no existe.")
        return value


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_method_id = serializers.IntegerField()

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        if not user.is_authenticated:
            raise serializers.ValidationError("Debes estar autenticado.")

        client, _ = Client.objects.get_or_create(user=user)
        data["client"] = client

        # validate address
        if not Address.objects.filter(id=data["address_id"], client=client).exists():
            raise serializers.ValidationError("Dirección inválida.")

        # validate payment method
        if not PaymentMethod.objects.filter(id=data["payment_method_id"]).exists():
            raise serializers.ValidationError("Método de pago inválido.")

        return data


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "book", "book_title", "quantity", "price", "subtotal"]

    subtotal = serializers.SerializerMethodField()

    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "client", "address", "payment_method", "status",
            "total_amount", "items", "created_at", "updated_at"
        ]
        read_only_fields = ["client", "total_amount", "status"]
