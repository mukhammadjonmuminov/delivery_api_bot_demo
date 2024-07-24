# cargo/urls.py
from django.urls import path
from .views import CargoListCreate, CargoDetail, CargoAssign

urlpatterns = [
    path('', CargoListCreate.as_view(), name='cargo-list-create'),
    path('<int:pk>/', CargoDetail.as_view(), name='cargo-detail'),
    path('<int:pk>/assign/', CargoAssign.as_view(), name='cargo-assign'),

]

