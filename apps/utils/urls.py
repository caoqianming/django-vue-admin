from django.urls import path, include
from rest_framework import routers
from apps.utils.views import SignatureViewSet
API_BASE_URL = 'api/utils/'

router = routers.DefaultRouter()
router.register('signature', SignatureViewSet, basename='signature')

urlpatterns = [
    path(API_BASE_URL, include(router.urls)),
]
