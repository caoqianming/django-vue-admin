from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Course, Card, StudyMaterial, Lesson, Tag, EnumConfig
from .serializers import CourseSerializer, CardListSerializer, StudyMaterialListSerializer, LessonListSerializer, \
    TagSerializer, \
    StudyMaterialDetailSerializer, CardDetailSerializer, LessonDetailSerializer, EnumConfigSerializer


class CourseViewSet(ModelViewSet):
    """
    课程-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = None
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type']

    # def get_queryset(self):
    #     all = self.request.query_params.get('all', True)
    #     return Course.objects.get_queryset(all=all)


class LessonViewSet(ModelViewSet):
    """
    课时-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Lesson.objects.all()
    serializer_class = LessonListSerializer
    pagination_class = None
    search_fields = ['title', 'version', 'course_id__title', 'group_name']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['course_id', 'type']

    def get_serializer_class(self):
        # 如果是根据ID查询详情，则使用详细查询序列化器
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return self.serializer_class


class CardViewSet(ModelViewSet):
    """
    卡片-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Card.objects.all()
    serializer_class = CardListSerializer
    pagination_class = None
    search_fields = ['title', 'group_name', 'topic']
    ordering_fields = ['pk']
    ordering = ['pk']
    filterset_fields = ['type', 'difficulty']

    def get_serializer_class(self):
        # 如果是根据ID查询详情，则使用详细查询序列化器
        if self.action == 'retrieve':
            return CardDetailSerializer
        return self.serializer_class


class StudyMaterialViewSet(ModelViewSet):
    """
    学习素材-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialListSerializer
    pagination_class = None
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']
    filterset_fields = ['type']

    def get_serializer_class(self):
        # 如果是根据ID查询详情，则使用详细查询序列化器
        if self.action == 'retrieve':
            return StudyMaterialDetailSerializer
        return self.serializer_class


class TagViewSet(ModelViewSet):
    """
    标签-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    search_fields = ['name', 'value', 'module', 'service']
    ordering_fields = ['pk']
    ordering = ['pk']


class EnumConfigViewSet(ModelViewSet):
    """
    枚举配置-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = EnumConfig.objects.all()
    serializer_class = EnumConfigSerializer
    pagination_class = None
    search_fields = ['name', 'module', 'service', 'value']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['module', 'service']
