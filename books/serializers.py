from rest_framework import serializers
from .models import Authors, Books, Category, BookCategory


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = ['id', 'olid', 'name', 'bio', 'birth_date', 'death_date']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent']


class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = ['id', 'book', 'category']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = [
            'id', 'olid', 'isbn_10', 'isbn_13', 'title', 'subtitle',
            'published_year', 'pages', 'language', 'cover_url', 'price', 'stock'
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(source="authors", many=True, read_only=True)
    categories = CategorySerializer(source="categories", many=True, read_only=True)

    class Meta:
        model = Books
        fields = [
            'id', 'olid', 'isbn_10', 'isbn_13',
            'title', 'subtitle', 'description',
            'published_year', 'pages', 'language',
            'cover_url', 'price', 'stock',
            'authors', 'categories'
        ]
