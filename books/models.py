from django.db import models
from django.utils.text import slugify

class Authors(models.Model):
    olid = models.CharField(unique=True, max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.CharField(max_length=50, blank=True, null=True)
    death_date = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'authors'

    def __str__(self):
        return self.name or ""


class Books(models.Model):
    olid = models.CharField(unique=True, max_length=50, blank=True, null=True)
    isbn_10 = models.CharField(max_length=20, blank=True, null=True)
    isbn_13 = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    published_year = models.CharField(max_length=20, blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    cover_url = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'books'

    def __str__(self):
        return self.title or ""

    @property
    def categories(self):
        return Category.objects.filter(bookcategory__book=self)

    @property
    def authors(self):
        return Authors.objects.filter(authorbook__book=self)


class AuthorBook(models.Model):
    author = models.ForeignKey('Authors', models.DO_NOTHING, blank=True,null=True, related_name='books')
    book = models.ForeignKey('Books',models.DO_NOTHING,blank=True,null=True,related_name='authors')

    class Meta:
        managed = False
        db_table = 'author_book'
        unique_together = ('author', 'book')


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,related_name='subcategories')

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def books(self):
        return Books.objects.filter(bookcategory__category=self)


class BookCategory(models.Model):
    book = models.ForeignKey('Books', on_delete=models.CASCADE, db_column='book_id', related_name='book_categories')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_column='category_id', related_name='category_books')

    class Meta:
        db_table = 'book_category'
        unique_together = ('book', 'category')