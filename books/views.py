from rest_framework import generics
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Books, Category, Authors
from .serializers import (
    BookSerializer, BookDetailSerializer,
    CategorySerializer, AuthorSerializer
)


class BookListView(generics.ListAPIView):
    queryset = Books.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Search
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(subtitle__icontains=search) |
                Q(isbn_10__icontains=search) |
                Q(isbn_13__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get("ordering")
        allowed = ["price", "-price", "published_year", "-published_year", "title", "-title"]
        if ordering in allowed:
            qs = qs.order_by(ordering)

        return qs

class BookDetailView(generics.RetrieveAPIView):
    queryset = Books.objects.all()
    serializer_class = BookDetailSerializer


class BookSimilarView(APIView):
    def get(self, request, pk):
        book = get_object_or_404(Books, pk=pk)
        categories = book.categories.all()

        qs = Books.objects.filter(
            book_categories__category__in=categories
        ).exclude(id=book.id).distinct()[:10]

        serializer = BookSerializer(qs, many=True)
        return Response(serializer.data)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class CategoryBooksView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return category.books()
    

class AuthorListView(generics.ListAPIView):
    queryset = Authors.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(bio__icontains=search)
            )
        return qs

class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Authors.objects.all()
    serializer_class = AuthorSerializer


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