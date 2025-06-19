
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class JewelryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class JewelryItem(models.Model):
    MATERIAL_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
    ]

    GENDER_CHOICES = [
        ('unisex', 'Unisex'),
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    category = models.ForeignKey(JewelryCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default='gold')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.FloatField(help_text="Weight in grams")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Field Option: auto_now_add



    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = "Прикраса"
        verbose_name_plural = "Прикраси"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product_detail', args=[self.id, self.slug])

class CustomUser(AbstractUser):

    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефону")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адреса")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Фото профілю")

    # Не обов'язково, але можна змінити порядок полів в адмін-панелі
    class Meta(AbstractUser.Meta):
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
        # ordering = ['username'] # Приклад сортування

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",  # <--- ДОДАЙТЕ ЦЕЙ related_name
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions_set",  # <--- ДОДАЙТЕ ЦЕЙ related_name
        related_query_name="customuser_permissions",
    )

    # ...
    def __str__(self):
        return self.username

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Користувач")
    # Якщо користувач не зареєстрований, будемо використовувати сесію
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True) # Для неавторизованих користувачів
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"
        ordering = ['-created_at']


    def __str__(self):
        if self.user:
            return f"Кошик користувача {self.user.username}"
        return f"Кошик (ID: {self.id})"


    def get_total_price(self):
        return sum(item.get_total_item_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name="Кошик")
    product = models.ForeignKey(JewelryItem, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна на момент додавання") # Ціна, за якою товар був доданий в кошик

    class Meta:
        verbose_name = "Елемент кошика"
        verbose_name_plural = "Елементи кошика"
        # Забезпечує, що в одному кошику не може бути двох однакових товарів
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} в кошику {self.cart.id}"

    def get_total_item_price(self):
        return self.price_at_addition * self.quantity


from django.conf import settings

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Користувач")
    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    last_name = models.CharField(max_length=50, verbose_name="Прізвище")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=250, verbose_name="Адреса (вулиця, будинок)")
    address_line2 = models.CharField(max_length=250, blank=True, verbose_name="Адреса (квартира/офіс)", help_text="Номер квартири, офісу або корпусу (за наявності)") # НОВЕ ПОЛЕ
    postal_code = models.CharField(max_length=20, verbose_name="Поштовий індекс")
    city = models.CharField(max_length=100, verbose_name="Місто")
    region = models.CharField(max_length=100, blank=True, verbose_name="Область/Регіон") # НОВЕ ПОЛЕ
    country = models.CharField(max_length=100, default='Україна', verbose_name="Країна") # НОВЕ ПОЛЕ, з defaul
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефону")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    paid = models.BooleanField(default=False, verbose_name="Оплачено")

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Замовлення")
    product = models.ForeignKey(JewelryItem, related_name='order_items', on_delete=models.CASCADE, verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за одиницю")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елементи замовлення"

    def __str__(self):
        return f'{self.id}'

    def get_cost(self):
        return self.price * self.quantity