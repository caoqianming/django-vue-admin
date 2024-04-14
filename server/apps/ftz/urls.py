from django.urls import path, include
from rest_framework import routers

from .views import CourseViewSet, LessonViewSet, CardViewSet, StudyMaterialViewSet, TagViewSet

router = routers.DefaultRouter()
router.register('course', CourseViewSet, basename='course')
router.register('lesson', LessonViewSet, basename='lesson')
router.register('card', CardViewSet, basename='card')
router.register('material', StudyMaterialViewSet, basename='material')
router.register('tag', TagViewSet, basename='tag')
urlpatterns = [
    path('', include(router.urls)),
]
