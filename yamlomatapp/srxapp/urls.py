from django.urls import path
from srxapp import views


app_name = "srxapp"
urlpatterns = [
    path("", views.main_view,
         name="main_view"),
    path("createconfigsession/", views.create_config_session,
         name="create_config_session"),
    path("loadcontent/createmodal/", views.loadcontent_createmodal,
         name="loadcontent_createmodal"),
    path("search/object/", views.search_object,
         name="search_object"),
    path("loadobjects/", views.load_objects,
         name="load_objects"),
    path("loadpolicy/", views.get_existing_policy_details,
         name="get_existing_policy_details"),
    path("getyamlconfig/", views.get_yamlconfig,
         name="get_yamlconfig"),
    path("writeconfig/", views.write_config,
         name="write_config"),
    path("filterobjects/", views.filter_objects,
         name="filter_objects"),
    path("policy/rename/", views.policy_rename,
         name="policy_rename"),
    path("policy/add/address/", views.policy_add_address,
         name="policy_add_address"),
    path("policy/add/application/", views.policy_add_application,
         name="policy_add_application"),
    path("policy/delete/address/", views.policy_delete_address,
         name="policy_delete_address"),
    path("policy/delete/application/", views.policy_delete_application,
         name="policy_delete_application"),
    path("object/create/address/", views.object_create_address,
         name="object_create_address"),
    path("object/create/addrset/", views.object_create_addrset,
         name="object_create_addrset"),
    path("object/create/application/", views.object_create_application,
         name="object_create_application"),
    path("object/create/appset/", views.object_create_appset,
         name="object_create_appset"),
]
