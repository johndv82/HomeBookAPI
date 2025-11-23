from django.urls import path
from .views import (
    ShippingListView,
    ShippingDetailView,
)

urlpatterns = [
    path("shipping/", ShippingListView.as_view(), name="shipping-list"),
    path("shipping/<int:pk>/", ShippingDetailView.as_view(), name="shipping-detail"),
]
