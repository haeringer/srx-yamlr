from django.urls import path, include
from django.views.generic import TemplateView
from . import views


app_name = 'cgapp'
urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('load/', TemplateView.as_view(template_name='cgapp/load.html'),
         name='load'),
    path('', views.mainView, name='mainView'),
    path('ajax/add-address-to-policy/', views.add_address_to_policy,
         name='add_address_to_policy'),
    path('ajax/add-application-to-policy/', views.add_application_to_policy,
         name='add_application_to_policy'),
    path('ajax/loadobjects/', views.loadobjects, name='loadobjects'),
    path('ajax/updatepolicy/', views.updatepolicy, name='updatepolicy'),
    path('ajax/newobject/', views.newobject, name='newobject'),
    path('ajax/filterobjects/', views.filterobjects, name='filterobjects'),
]
