from django.urls import path
from .views import (
    ClientMeView,
    AddressListView,
    AddressDetailView,
)

urlpatterns = [
    path("client/me/", ClientMeView.as_view(), name="client-me"),

    #CRUD addresses
    path("addresses/", AddressListView.as_view(), name="address-list"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
]
