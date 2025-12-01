from rest_framework import viewsets
from books.models import Authors, Category, Books
from .serializers import AuthorSerializer, CategorySerializer, BookSerializer
from rest_framework.permissions import AllowAny

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Authors.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
