from django.urls import path
from .views import register,login, get_facilities,get_facilities3

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('facilities/', get_facilities),
]
