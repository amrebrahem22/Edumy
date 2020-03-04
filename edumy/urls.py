from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from courses.views import index, search_view, about
from instructors.views import InstructorListView, InstructorDetailView
from contact.views import contactview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="home"),
    path('search/', search_view, name="search"),
    path('contact/', contactview, name="contact"),
    path('about/', about, name='about'),
    path('instructors/', InstructorListView.as_view(), name="instructors"),
    path('instructors/<pk>/', InstructorDetailView.as_view(), name="instructor"),
    path('courses/', include('courses.urls')),
    path('auth/', include('instructors.urls')),
    path('cart/', include('cart.urls')),
    path('blog/', include('blog.urls')),
    path('events/', include('events.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
