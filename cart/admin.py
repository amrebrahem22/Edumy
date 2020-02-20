from django.contrib import admin
from .models import OrderItem, Order, Payment

admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Payment)
