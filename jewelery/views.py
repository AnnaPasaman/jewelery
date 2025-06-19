from django.shortcuts import render, redirect, get_object_or_404
from .models import JewelryItem, Cart, CartItem, Order, OrderItem
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from .forms import OrderCreateForm
from decimal import Decimal
import uuid


def product_list(request):
    products = JewelryItem.objects.all()
    return render(request, 'jewelery/products.html', {'products': products})
def index(request):
    context = {'title': 'Головна сторінка'}
    return render(request, 'jewelery/index.html', context)

def view1(request):
    context = {'title': 'Сторінка 1'}
    return render(request, 'jewelery/view1.html', context)

def view2(request):
    context = {'title': 'Сторінка 2'}
    return render(request, 'jewelery/view2.html', context)

def view3(request):
    context = {'title': 'Сторінка 3'}
    return render(request, 'jewelery/view3.html', context)

def view4(request):
    context = {'title': 'Сторінка 4'}
    return render(request, 'jewelery/view4.html', context)

def view5(request):
    context = {'title': 'Сторінка 5'}
    return render(request, 'jewelery/view5.html', context)

def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    else:
        session_key = request.session.session_key or str(uuid.uuid4())
        request.session['anon_user'] = session_key
        cart, created = Cart.objects.get_or_create(session_id=session_key, is_active=True)
    return cart

# 1. Сторінка з каталогом товарів (модифікуємо існуючу)
def product_list_view(request):
    products = JewelryItem.objects.filter(available=True)
    return render(request, 'jewelery/view1.html', {'products': products})

# 3. Деталі кошика
def cart_detail(request):
    cart = None
    cart_items = []
    total_price = Decimal('0.00')

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.get('cart_session_key')
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()

    if cart:
        cart_items = cart.items.all()
        total_price = cart.get_total_price()

    return render(request, 'jewelery/view1.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price
    })

# 4. Оновлення кількості товару в кошику
@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    new_quantity = int(request.POST.get('quantity'))

    if new_quantity > 0:
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.info(request, f"Кількість '{cart_item.product.name}' оновлено.")
    else:
        cart_item.delete()
        messages.warning(request, f"'{cart_item.product.name}' видалено з кошика.")

    return redirect('cart_detail')

# 5. Видалення товару з кошика
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    product_name = cart_item.product.name # Зберігаємо назву для повідомлення
    cart_item.delete()
    messages.warning(request, f"'{product_name}' видалено з кошика.")
    return redirect('cart_detail')

# 6. Оформлення замовлення
def order_create_view(request):
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.get('cart_session_key')
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()

    if not cart or not cart.items.exists():
        messages.warning(request, "Ваш кошик порожній. Додайте товари перед оформленням замовлення.")
        return redirect('product_list') # Або інша сторінка

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic(): # Використовуємо транзакцію для атомарності операції
                order = form.save(commit=False)
                order.user = request.user if request.user.is_authenticated else None
                order.save()

                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product_name=cart_item.product.name,
                        product_price=cart_item.price_at_addition,
                        quantity=cart_item.quantity
                    )
                # Очистити кошик після створення замовлення
                cart.items.all().delete()
                if not request.user.is_authenticated:
                    if 'cart_session_key' in request.session:
                        del request.session['cart_session_key']
                    # Додатково: видалити сам об'єкт Cart, якщо він був тільки для сесії
                    cart.delete()


                messages.success(request, f"Ваше замовлення #{order.id} успішно оформлено!")
                # Перенаправити на сторінку підтвердження замовлення
                return redirect('order_confirmation', order_id=order.id)
        else:
            messages.error(request, "Будь ласка, виправте помилки у формі.")
    else:
        # Заповнити форму даними користувача, якщо він зареєстрований
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                # Додайте інші поля, якщо вони є у моделі User та вам потрібні
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'jewelery/view1.html', {
        'cart': cart, # Може бути порожнім, якщо кошик вже був порожній
        'cart_items': cart.items.all() if cart else [], # Щоб показати товари в кошику на сторінці оформлення
        'total_price': cart.get_total_price() if cart else Decimal('0.00'),
        'form': form
    })

# 7. Сторінка підтвердження замовлення (проста)


def order_create(request):
        cart = Cart(request)
        if not cart:
            messages.error(request, 'Ваш кошик порожній. Додайте товари, щоб оформити замовлення.')
            return redirect('product_list')

        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )

                cart.clear()
                messages.success(request, 'Ваше замовлення успішно оформлено!')
                return redirect('order_confirmation', order_id=order.id)

        else:
            # Попереднє заповнення форми з даних користувача
            initial_data = {}
            if request.user.is_authenticated:
                initial_data['first_name'] = request.user.first_name
                initial_data['last_name'] = request.user.last_name
                initial_data['email'] = request.user.email
            form = OrderCreateForm(initial=initial_data)

        return render(request, 'jewelery/view5.html', {'form': form, 'cart': cart})


        # def order_create(request):
#     cart = Cart(request)
#     if not cart:
#         messages.error(request, 'Ваш кошик порожній. Додайте товари, щоб оформити замовлення.')
#         return redirect('product_list')
#
#     if request.method == 'POST':
#         form = OrderCreateForm(request.POST)
#         if form.is_valid():
#             order = form.save(commit=False)
#             if request.user.is_authenticated:
#                 order.user = request.user
#             order.save()
#
#             for item in cart:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item['product'],
#                     price=item['price'],
#                     quantity=item['quantity']
#                 )
#
#             cart.clear()
#             messages.success(request, 'Ваше замовлення успішно оформлено!')
#             return redirect('order_confirmation', order_id=order.id)
#
#     else:
#         initial_data = {}
#         if request.user.is_authenticated:
#              Заповнюємо дані, якщо користувач авторизований
#             initial_data = {
#                 'first_name': request.user.first_name,
#                 'last_name': request.user.last_name,
#                 'email': request.user.email,
#                 'phone_number': getattr(request.user, 'phone_number', ''), # Припустимо, CustomUser має phone_number
#                 'country': getattr(request.user, 'country', ''), # Якщо CustomUser має це поле
#                 'city': getattr(request.user, 'city', ''),
#                 'region': getattr(request.user, 'region', ''),
#                 'postal_code': getattr(request.user, 'postal_code', ''),
#                 'address': getattr(request.user, 'address', ''),
#                 'address_line2': getattr(request.user, 'address_line2', ''),
#             }
#         form = OrderCreateForm(initial=initial_data)
#
#     context = {
#         'form': form,
#         'cart_items': cart,
#         'total_price': cart.get_total_price(),
#         'title': 'Оформлення Замовлення'
#     }
#     return render(request, 'jewelery/view5.html', context)


    # ...

from django.contrib.auth.decorators import login_required # Для захисту сторінки

@login_required
def user_profile_view(request):
    """
    Відображає сторінку профілю користувача.
    """
    user = request.user
    # Отримуємо замовлення поточного користувача
    orders = Order.objects.filter(user=user).order_by('-created')

    context = {
        'title': f'Профіль {user.username}',
        'orders': orders,

    }
    return render(request, 'jewelery/view5.html', context)
# jewelery/views.py
# Переконайтеся, що OrderItem також імпортовано

# ... інші ваші в'юшки ...

@login_required # Розкоментуйте, якщо в'юшка має бути доступна тільки для авторизованих користувачів
def order_confirmation_view(request, order_id):
    """
    Відображає сторінку підтвердження замовлення.
    """
    try:
        # Отримуємо об'єкт замовлення за ID.
        # Якщо замовлення не існує, Django автоматично поверне 404 помилку.
        order = get_object_or_404(Order, id=order_id)

        # Додаткова логіка безпеки:
        # 1. Якщо користувач авторизований, переконайтеся, що замовлення належить йому.
        if request.user.is_authenticated:
            # Якщо замовлення має прив'язаного користувача, і це не поточний користувач,
            # або якщо користувач є власником замовлення, то дозволити доступ.
            # Якщо user=None (незареєстрований користувач), то цю перевірку пропускаємо.
            if order.user and order.user != request.user:
                return redirect('product_list') # Або будь-яка інша сторінка, наприклад, 'access_denied'

        # 2. Можна також додати перевірку, що замовлення "оплачене",
        # щоб не показувати незавершені замовлення після їх створення.
        # if not order.paid:
        #     # Можливо, перенаправити на сторінку оплати або просто не показувати
        #     return redirect('product_list') # Або інший URL

        # Отримуємо всі елементи замовлення, пов'язані з цим замовленням
        order_items = order.items.all() # Припускаємо, що related_name для ForeignKey на OrderItem дорівнює 'items'

        # Контекст для передачі даних у шаблон
        context = {
            'order': order,
            'order_items': order_items,
        }

        # Рендеримо шаблон, передаючи йому об'єкт замовлення та його елементи
        return render(request, 'jewelery/view5.html', context)

    except Exception as e:
        # Обробка інших можливих помилок, наприклад, логування
        print(f"Помилка при відображенні підтвердження замовлення {order_id}: {e}")
        # Можна перенаправити на сторінку помилки або на головну
        return redirect('product_list') # Перенаправлення у випадку непередбаченої помилки

# jewelery/forms.py
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(JewelryItem, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Некоректна кількість товару.")
        return redirect('product_list')

    cart = _get_or_create_cart(request)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f"Кількість '{product.name}' оновлено в кошику.")
    except CartItem.DoesNotExist:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            price_at_addition=product.price
        )
        messages.success(request, f"'{product.name}' додано до кошика.")

    return redirect('cart_detail')
def product_detail(request, product_id):
    product = get_object_or_404(JewelryItem, id=product_id)
    return render(request, 'jewelery/product_detail.html', {'product': product})
@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, "Профіль успішно оновлено.")
        return redirect('index')
    return render(request, 'jewelery/edit_profile.html')







# Ваша форма CustomUserChangeForm
