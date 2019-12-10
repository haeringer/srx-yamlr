from django.urls import path
from srxpolsrch import views

app_name = "srxpolsrch"
urlpatterns = [
    path("", views.main_view,
         name="main_view"),
]
