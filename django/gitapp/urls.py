from django.urls import path
from . import views


app_name = "gitapp"
urlpatterns = [
    path("clonerepo/", views.clone_repo,
         name="clone_repo"),
    path("diff/", views.get_diff,
         name="get_diff"),
    path("commithash/", views.commithash,
         name="commithash"),
    path("commitconfig/", views.commit_config,
         name="commit_config"),
]
