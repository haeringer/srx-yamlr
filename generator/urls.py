from django.urls import path
from . import views


app_name = 'generator'
urlpatterns = [
    path('', views.index, name='index'),
    path('getaddressdata/', views.getaddressdata, name='getaddressdata'),
    path('getapplicationdata/', views.getapplicationdata, name='getapplicationdata'),
]