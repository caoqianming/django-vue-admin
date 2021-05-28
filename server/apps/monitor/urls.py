from django.urls import path, include
from rest_framework import routers
from .views import ServerInfoView, LogView, LogDetailView


urlpatterns = [
    path('log/', LogView.as_view()),
    path('log/<str:name>/', LogDetailView.as_view()),
    path('server/', ServerInfoView.as_view()),
]
