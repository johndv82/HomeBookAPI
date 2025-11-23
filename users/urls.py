from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, AddressViewSet

router = DefaultRouter()

router.register(r"clients", ClientViewSet, basename="clients")
router.register(r"addresses", AddressViewSet, basename="address")

urlpatterns = router.urls
