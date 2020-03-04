from django.urls import path
from .views import PostListView, PostDetailView, PostCreate, PostUpdate, PostDelete

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='list'),
    path('create/', PostCreate.as_view(), name='create'),
    path('<slug>/', PostDetailView.as_view(), name='detail'),
    path('<slug>/update/', PostUpdate.as_view(), name='update'),
    path('<slug>/delete/', PostDelete.as_view(), name='delete'),
]

