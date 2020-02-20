from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from courses.views import index
from instructors.views import InstructorListView, InstructorDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="home"),
    path('instructors/', InstructorListView.as_view(), name="instructors"),
    path('instructors/<pk>/', InstructorDetailView.as_view(), name="instructor"),
    path('courses/', include('courses.urls')),
    path('auth/', include('instructors.urls')),
    path('cart/', include('cart.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
