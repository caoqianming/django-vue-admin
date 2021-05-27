from django.urls import path, include
from rest_framework import routers
from .views import ServerInfo
urlpatterns = [
    path('server/', ServerInfo.as_view()),
]
