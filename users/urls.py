from django.urls import path
from .views import UserCreate, UserList

urlpatterns = [
    path('register/', UserCreate.as_view(), name='user-register'),
    path('', UserList.as_view(), name='user-list'),
]
