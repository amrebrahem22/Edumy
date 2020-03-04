from django.urls import path
from .views import EventListView, EventDetailView, EventCreate, EventUpdate, EventDelete

app_name = 'events'

urlpatterns = [
    path('', EventListView.as_view(), name='list'),
    path('create/', EventCreate.as_view(), name='create'),
    path('<slug>/', EventDetailView.as_view(), name='detail'),
    path('<slug>/update/', EventUpdate.as_view(), name='update'),
    path('<slug>/delete/', EventDelete.as_view(), name='delete'),
]

