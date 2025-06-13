
from django.db import models


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

    def __str__(self):
        return f"{self.name} ({self.material})"

