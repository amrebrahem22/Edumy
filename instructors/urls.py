from django.urls import path
from .views import login_view, logout_view, signup, become_instructor

app_name='auth'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout_view, name='logout'),
    
    path('become-instructor/', become_instructor, name='become_instructor'),
]
