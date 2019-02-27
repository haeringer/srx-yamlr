from django.urls import path

from srxapp import consumers


websocket_urlpatterns = [
    path('ws/deploy/', consumers.DeploymentConsumer),
    path('ws/check/', consumers.CheckConsumer),
]
