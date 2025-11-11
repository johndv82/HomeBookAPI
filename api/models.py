from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


# ==========================================================
# MODELOS YA EXISTENTES EN LA BD
# ==========================================================

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
        """Acceso directo a categorías (relación N:M)"""
        return Category.objects.filter(bookcategory__book=self)


class AuthorBook(models.Model):
    author = models.ForeignKey('Authors', models.DO_NOTHING, blank=True, null=True)
    book = models.ForeignKey('Books', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'author_book'


# ==========================================================
# CATEGORÍAS DE LIBROS
# ==========================================================

class Category(models.Model):
    """Categorías de libros (con jerarquía opcional)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def books(self):
        """Devuelve todos los libros de esta categoría"""
        return Books.objects.filter(bookcategory__category=self)


class BookCategory(models.Model):
    """Tabla intermedia N:M entre Books y Category"""
    book = models.ForeignKey('Books', on_delete=models.CASCADE, db_column='book_id')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_column='category_id')

    class Meta:
        db_table = 'book_category'
        unique_together = ('book', 'category')


# ==========================================================
# USUARIOS Y CLIENTES
# ==========================================================

class User(AbstractUser):
    """Usuario base para autenticación con Djoser"""
    email = models.EmailField(unique=True)
    is_client = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class Client(models.Model):
    """Perfil extendido del cliente"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'clients'

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Address(models.Model):
    """Direcciones de envío del cliente"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Perú")
    phone = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'addresses'

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# ==========================================================
# CARRITO DE COMPRAS
# ==========================================================

class Cart(models.Model):
    """Carrito de compras"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart #{self.id} - {self.client.user.email}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class CartItem(models.Model):
    """Items dentro del carrito"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'book')

    def subtotal(self):
        return (self.book.price or 0) * self.quantity


# ==========================================================
# ÓRDENES Y PAGOS
# ==========================================================

class PaymentMethod(models.Model):
    """Métodos de pago disponibles"""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'payment_methods'

    def __str__(self):
        return self.name


class Order(models.Model):
    """Orden de compra"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order #{self.id} - {self.client.user.email}"


class OrderItem(models.Model):
    """Detalle de cada producto en la orden"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Books, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'

    def subtotal(self):
        return self.price * self.quantity


# ==========================================================
# ENVÍOS
# ==========================================================

class Shipping(models.Model):
    """Datos de envío asociados a la orden"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'shipping'

    def __str__(self):
        return f"Shipping for Order #{self.order.id}"
