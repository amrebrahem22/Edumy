from django.urls import path
from .views import (
    CoursesListView,
    CoursesDetailView,
    course_create,
    course_create_chapter,
    course_create_lesson,
    my_courses,
    category,
    add_to_wishlist,
    wish_list
)

app_name = 'courses'

urlpatterns = [
    path('', CoursesListView.as_view(), name='index'),
    path('categories/<slug>/', category, name='category'),
    path('create/', course_create, name='course_create'),
    path('my-courses/', my_courses, name='my_courses'),
    path('my-wishlist/', wish_list, name='wishlist'),
    path('create/<course_id>/create-chapter/', course_create_chapter, name='course_create_chapter'),
    path('create/<course_id>/create-lesson/', course_create_lesson, name='course_create_lesson'),
    path('<slug>/', CoursesDetailView.as_view(), name='detail'),
    path('add_to_wishlist/<slug>/', add_to_wishlist, name='add_to_wishlist'),
]
