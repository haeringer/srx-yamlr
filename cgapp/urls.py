from django.urls import path, include
from django.views.generic import TemplateView
from . import views


app_name = 'cgapp'
urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('load/', TemplateView.as_view(template_name='cgapp/load.html'),
         name='load'),
    path('', views.mainView, name='mainView'),
    path('ajax/policy-add-address/', views.policy_add_address,
         name='policy_add_address'),
    path('ajax/policy-delete-address/', views.policy_delete_address,
         name='policy_delete_address'),
    path('ajax/policy-add-application/', views.policy_add_application,
         name='policy_add_application'),
    path('ajax/policy-delete-application/', views.policy_delete_application,
         name='policy_delete_application'),
    path('ajax/loadobjects/', views.loadobjects, name='loadobjects'),
    path('ajax/newobject/', views.newobject, name='newobject'),
    path('ajax/filterobjects/', views.filterobjects, name='filterobjects'),
]
