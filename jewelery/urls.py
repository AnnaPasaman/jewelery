from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('view2/', views.view2, name='order_create'),
    path('view3/', views.view3, name='view3'),
    path('view4/', views.view4, name='view4'),
    path('user/', views.user_profile_view, name='user_profile'),
    path('products/', views.product_list, name='product_list'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('order/create/', views.order_create, name='order_create'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
]
