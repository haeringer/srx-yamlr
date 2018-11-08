from django.urls import path
from . import views


app_name = 'generator'
urlpatterns = [
    path('', views.index, name='index'),
    path('getparentzone/', views.getparentzone, name='getparentzone'),
]