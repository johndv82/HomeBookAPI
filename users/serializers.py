from rest_framework import serializers
from .models import User, Client, Address


class UserSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura (Djoser maneja creación)"""
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "is_client", "is_admin"
        ]
        read_only_fields = ["id", "is_client", "is_admin"]


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Client
        fields = ["id", "user", "phone", "birth_date"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "client",
            "full_name",
            "address_line",
            "city",
            "state",
            "postal_code",
            "country",
            "phone",
            "is_default",
        ]
        read_only_fields = ["client"]
