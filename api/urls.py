from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.urls")),
    path("books/", include("books.urls")),
    #path("orders/", include("orders.urls")),
    #path("payments/", include("payments.urls")),
    #path("shippings/", include("shippings.urls")),
]