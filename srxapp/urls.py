from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from srxapp import views
from srxapp import forms


app_name = 'srxapp'
urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/login/', auth_views.LoginView.as_view(
         authentication_form=forms.LoginForm)),  # override default login form
    path('', views.main_view,
         name='main_view'),
    path('load/', TemplateView.as_view(template_name='srxapp/load.html'),
         name='load'),
    path('ajax/loadobjects/', views.load_objects,
         name='load_objects'),
    path('ajax/loadpolicy/', views.get_existing_policy_details,
         name='get_existing_policy_details'),
    path('ajax/getyamlconfig/', views.get_yamlconfig,
         name='get_yamlconfig'),
    path('ajax/filterobjects/', views.filter_objects,
         name='filter_objects'),
    path('ajax/policy/rename/', views.policy_rename,
         name='policy_rename'),
    path('ajax/policy/add/address/', views.policy_add_address,
         name='policy_add_address'),
    path('ajax/policy/add/application/', views.policy_add_application,
         name='policy_add_application'),
    path('ajax/policy/delete/address/', views.policy_delete_address,
         name='policy_delete_address'),
    path('ajax/policy/delete/application/', views.policy_delete_application,
         name='policy_delete_application'),
    path('ajax/object/create/address/', views.object_create_address,
         name='object_create_address'),
    path('ajax/object/create/addrset/', views.object_create_addrset,
         name='object_create_addrset'),
    path('ajax/object/create/application/', views.object_create_application,
         name='object_create_application'),
    path('ajax/object/create/appset/', views.object_create_appset,
         name='object_create_appset'),
    path('ajax/settings/token/gogs/', views.set_token_gogs,
         name='set_token_gogs'),
]
