
from django import forms
from .models import Order, CustomUser
from django.contrib.auth.forms import UserChangeForm


COUNTRIES = [
    ('Україна', 'Україна'), ('Польща', 'Польща'), ('Німеччина', 'Німеччина'),
    ('США', 'США'), ('Канада', 'Канада'),
]

REGIONS_UKRAINE = [
    ('', 'Оберіть область (необов\'язково)'), # Додано пустий вибір
    ('Вінницька область', 'Вінницька область'),
    ('Волинська область', 'Волинська область'),
    ('Дніпропетровська область', 'Дніпропетровська область'),
    ('Донецька область', 'Донецька область'),
    ('Житомирська область', 'Житомирська область'),
    ('Закарпатська область', 'Закарпатська область'),
    ('Запорізька область', 'Запорізька область'),
    ('Івано-Франківська область', 'Івано-Франківська область'),
    ('Київська область', 'Київська область'),
    ('Кіровоградська область', 'Кіровоградська область'),
    ('Луганська область', 'Луганська область'),
    ('Львівська область', 'Львівська область'),
    ('Миколаївська область', 'Миколаївська область'),
    ('Одеська область', 'Одеська область'),
    ('Полтавська область', 'Полтавська область'),
    ('Рівненська область', 'Рівненська область'),
    ('Сумська область', 'Сумська область'),
    ('Тернопільська область', 'Тернопільська область'),
    ('Харківська область', 'Харківська область'),
    ('Херсонська область', 'Херсонська область'),
    ('Хмельницька область', 'Хмельницька область'),
    ('Черкаська область', 'Черкаська область'),
    ('Чернівецька область', 'Чернівецька область'),
    ('Чернігівська область', 'Чернігівська область'),
    ('м. Київ', 'м. Київ'),
    ('м. Севастополь', 'м. Севастополь'),
    ('Автономна Республіка Крим', 'Автономна Республіка Крим'),
]


class CustomUserChangeForm(UserChangeForm):
    # Додаткові поля, які ми хочемо бачити у формі редагування профілю
    # Використовуємо ChoiceField для випадаючих списків, якщо потрібно
    country = forms.ChoiceField(
        choices=COUNTRIES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Країна",
        required=False
    )
    region = forms.ChoiceField(
        choices=REGIONS_UKRAINE,
        required=False, # Не обов'язкове поле
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Область/Регіон"
    )

    class Meta(UserChangeForm.Meta): # <--- Успадковуємо Meta від UserChangeForm.Meta
        model = CustomUser # <--- Модель, для якої призначена ця форма
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'country',  'region',
             'address',
        )
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Наприклад, +380XXXXXXXXX'}),
            # 'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше місто'}),
            # 'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поштовий індекс'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Вулиця, будинок'}),
            # 'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Квартира/офіс (необов\'язково)'}),
            # Для полів, що йдуть з AbstractUser (username, email, first_name, last_name),
            # можна також додати віджети, якщо потрібна custom-стилізація
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ваше ім'я"}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ваше прізвище"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "your@example.com"}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ім'я користувача (логін)"}),
        }
        # Виключаємо поля, які не мають бути редагованими через цю форму (наприклад, пароль)
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions')

class OrderCreateForm(forms.ModelForm):
    # Перевизначення полів для випадаючих списків у формі замовлення
    country = forms.ChoiceField(
        choices=COUNTRIES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Країна",
        initial='Україна'  # Значення за замовчуванням
    )
    region = forms.ChoiceField(
        choices=REGIONS_UKRAINE,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Область/Регіон"
    )

    class Meta:
        model = Order  # <--- Модель, для якої призначена ця форма
        fields = [
            'first_name', 'last_name', 'email',
            'phone_number',  # <--- !!! ВАЖЛИВО: 'phone_number', а не 'phone'
            'country', 'region',
            'address',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ваше ім'я"}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ваше прізвище"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "your@example.com"}),
            'phone_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Наприклад, +380XXXXXXXXX'}),
            # 'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Наприклад, Луцьк'}),
            'address': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Наприклад, вул. Головна, 10'}),
            # 'address_line2': forms.TextInput(
            #     attrs={'class': 'form-control', 'placeholder': 'Наприклад, кв. 5, офіс 2 (необов\'язково)'}),
            # 'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Наприклад, 01001'}),
        }
# jewelery/forms.py
class CartAddProductForm(forms.Form):
    # Кількість товару, мінімум 1
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control text-center', 'min': '1'}),
        label="Кількість"
    )
    # Поле для оновлення кошика: True - замінити кількість, False - додати до існуючої
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)






# Ваша форма CustomUserChangeForm
# ...