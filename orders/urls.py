from django.urls import path
from .views import (
    CartDetailView, AddToCartView, UpdateCartItemView, RemoveCartItemView,
    CheckoutView, OrderListView, OrderDetailView
)

urlpatterns = [
    # Cart
    path("cart/", CartDetailView.as_view(), name="cart-detail"),
    path("cart/add/", AddToCartView.as_view(), name="cart-add"),
    path("cart/item/<int:item_id>/", UpdateCartItemView.as_view(), name="cart-update"),
    path("cart/item/<int:item_id>/delete/", RemoveCartItemView.as_view(), name="cart-remove"),

    # Checkout
    path("checkout/", CheckoutView.as_view(), name="checkout"),

    # Orders
    path("", OrderListView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
