from django.urls import path
from srxpolsrch import views


app_name = "srxpolsrch"
urlpatterns = [
    path("", views.main_view,
         name="main_view"),
    path("search/", views.search,
         name="search"),
    path("getpolicyyaml/", views.get_policy_yaml,
         name="get_policy_yaml"),
]
