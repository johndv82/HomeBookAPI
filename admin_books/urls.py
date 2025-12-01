from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, CategoryViewSet, AuthorViewSet

router = DefaultRouter()

router.register(r'books', BookViewSet, basename='books')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'authors', AuthorViewSet, basename='authors')

urlpatterns = [
    path('', include(router.urls)),
]