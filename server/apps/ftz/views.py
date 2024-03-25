from rest_framework.viewsets import ModelViewSet

from .models import Course, Card, StudyMaterial, Lesson
from .serializers import CourseSerializer, CardSerializer, StudyMaterialSerializer, LessonSerializer


class CourseViewSet(ModelViewSet):
    """
    角色-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = None
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']

    def get_queryset(self):
        all = self.request.query_params.get('all', True)
        return Course.objects.get_queryset(all=all)


class LessonViewSet(ModelViewSet):
    """
    课时-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = None
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']


class CardViewSet(ModelViewSet):
    """
    卡片-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    pagination_class = None
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']


class StudyMaterialViewSet(ModelViewSet):
    """
    学习素材-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialSerializer
    pagination_class = None
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']
