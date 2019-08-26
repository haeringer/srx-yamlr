from django.urls import path
from . import views


app_name = "gitapp"
urlpatterns = [
    path("clonerepo/", views.clone_repo,
         name="clone_repo"),
    path("commitconfig/", views.commit_config,
         name="commit_config"),
]
