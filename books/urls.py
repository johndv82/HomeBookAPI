from django.urls import path
from .views import (BookListView, BookDetailView, BookSimilarView, 
CategoryListView, CategoryDetailView, CategoryBooksView, AuthorListView, AuthorDetailView)

urlpatterns = [
    path("books/", BookListView.as_view()),
    path("books/<int:pk>/", BookDetailView.as_view()),
    path("books/<int:pk>/similar/", BookSimilarView.as_view()),

    path("categories/", CategoryListView.as_view()),
    path("categories/<slug:slug>/", CategoryDetailView.as_view()),
    path("categories/<slug:slug>/books/", CategoryBooksView.as_view()),

    path("authors/", AuthorListView.as_view()),
    path("authors/<int:pk>/", AuthorDetailView.as_view()),
]