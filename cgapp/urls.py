from django.urls import path
from . import views


app_name = 'cgapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/objectdata/', views.objectdata, name='objectdata'),
    path('ajax/newobject/', views.newobject, name='newobject'),
]