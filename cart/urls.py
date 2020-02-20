from django.urls import path
from .views import add_to_cart, remove_from_cart, order, PaymentView

app_name = 'cart'

urlpatterns = [
    path('', order, name='order'),
    path('add-to-cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('payment/', PaymentView.as_view(), name='payment'),
]
