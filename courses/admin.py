from django.contrib import admin

from .models import Category, Course

admin.site.register(Course)
admin.site.register(Category)