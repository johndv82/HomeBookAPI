from django.urls import path
from .views import PaymentMethodListView, PaymentMethodDetailView

urlpatterns = [
    path("methods/", PaymentMethodListView.as_view(), name="payment-methods"),
    path("methods/<int:pk>/", PaymentMethodDetailView.as_view(), name="payment-method-detail"),
]
