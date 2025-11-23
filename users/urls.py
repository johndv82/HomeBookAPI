from rest_framework.routers import DefaultRouter
from .views import CurrentUserViewSet, ClientViewSet, AddressViewSet

router = DefaultRouter()

router.register(r"clients", ClientViewSet, basename="client")
router.register(r"addresses", AddressViewSet, basename="address")

urlpatterns = router.urls
