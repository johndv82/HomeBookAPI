from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Books, Authors, Category
from .serializers import (
    BookSerializer, BookDetailSerializer,
    CategorySerializer, AuthorSerializer
)

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'subtitle', 'isbn_10', 'isbn_13']
    ordering_fields = ['price', 'published_year', 'title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookSerializer

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        book = self.get_object()
        categories = book.categories
        qs = Books.objects.filter(
            book_categories__category__in=categories
        ).exclude(id=book.id).distinct()[:10]

        return Response(BookSerializer(qs, many=True).data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def books(self, request, slug=None):
        category = get_object_or_404(Category, slug=slug)
        qs = category.books()
        return Response(BookSerializer(qs, many=True).data)


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Authors.objects.all()
    serializer_class = AuthorSerializer
    search_fields = ['name', 'bio']

"""

from rest_framework import viewsets
from .models import Authors, Category, Books
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

"""