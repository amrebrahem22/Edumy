from django.urls import path
from .views import (
    CoursesListView,
    CoursesDetailView,
    course_create,
    course_create_chapter,
    course_create_lesson
)

app_name = 'courses'

urlpatterns = [
    path('', CoursesListView.as_view(), name='index'),
    path('create/', course_create, name='course_create'),
    path('create/<course_id>/create-chapter/', course_create_chapter, name='course_create_chapter'),
    path('create/<course_id>/create-lesson/', course_create_lesson, name='course_create_lesson'),
    path('<slug>/', CoursesDetailView.as_view(), name='detail'),
]
