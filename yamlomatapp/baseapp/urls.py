from django.urls import include, path
from django.contrib.auth import views as auth_views

from baseapp import views, forms


urlpatterns = [
    path("auth/login/", auth_views.LoginView.as_view(
         authentication_form=forms.LoginForm)),  # override default login form
    path("auth/", include("django.contrib.auth.urls")),
    path("", views.main_view,
         name="main_view"),
    path("session/status/", views.check_session_status,
         name="check_session_status"),
    path("session/extend/", views.extend_session,
         name="extend_session"),
    path("checktoken/gogs/", views.check_token_gogs,
         name="check_token_gogs"),
    path("settings/token/gogs/", views.set_token_gogs,
         name="set_token_gogs"),
    path("settings/password/change/", views.set_new_password,
         name="set_new_password"),
]
