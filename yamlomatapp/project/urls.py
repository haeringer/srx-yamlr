from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("baseapp.urls")),
    path("srx/", include("srxapp.urls")),
    path("git/", include("gitapp.urls")),
    path("admin/", admin.site.urls),
]
