from django.contrib import admin
from .models import JewelryCategory, JewelryItem

@admin.register(JewelryCategory)
class JewelryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')



@admin.register(JewelryItem)
class JewelryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'material', 'in_stock')
    list_filter = ('material', 'category', 'in_stock', 'gender')
    search_fields = ('description','name')






from django.contrib import admin

# Register your models here.
