import logging

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import (FileUploadParser, JSONParser,
                                    MultiPartParser)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError, ParseError
from utils.queryset import get_child_queryset2

from .filters import UserFilter
from .mixins import CreateUpdateModelAMixin, OptimizationMixin
from .models import (Dict, DictType, File, Organization, Permission, Position,
                     Role, User)
from .permission import RbacPermission, get_permission_list
from .permission_data import RbacFilterSet
from .serializers import (DictSerializer, DictTypeSerializer, FileSerializer,
                          OrganizationSerializer, PermissionSerializer,
                          PositionSerializer, RoleSerializer, PTaskSerializer,PTaskCreateUpdateSerializer,
                          UserCreateSerializer, UserListSerializer,
                          UserModifySerializer)

logger = logging.getLogger('log')
# logger.info('请求成功！ response_code:{}；response_headers:{}；response_body:{}'.format(response_code, response_headers, response_body[:251]))
# logger.error('请求出错-{}'.format(error))

from server.celery import app as celery_app
class TaskList(APIView):
    permission_classes = ()

    def get(self, requests):
        tasks = list(sorted(name for name in celery_app.tasks if not name.startswith('celery.')))
        return Response(tasks)

class LogoutView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):  # 可将token加入黑名单
        return Response(status=status.HTTP_200_OK)

class PTaskViewSet(OptimizationMixin, ModelViewSet):
    perms_map = {'get': '*', 'post': 'ptask_create',
                 'put': 'ptask_update', 'delete': 'ptask_delete'}
    queryset = PeriodicTask.objects.exclude(name__contains='celery.')
    serializer_class = PTaskSerializer
    search_fields = ['name']
    filterset_fields = ['enabled']
    ordering = ['-pk']

    @action(methods=['put'], detail=True, perms_map={'put':'task_update'},
            url_name='task_toggle')
    def toggle(self, request, pk=None):
        """
        修改启用禁用状态
        """
        obj = self.get_object()
        obj.enabled = False if obj.enabled else True
        obj.save()
        return Response(status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PTaskSerializer
        return PTaskCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        timetype = data.get('timetype', None)
        interval_ = data.get('interval_', None)
        crontab_ = data.get('crontab_', None)
        if timetype == 'interval' and interval_:
            data['crontab'] = None
            try:
                interval, _ = IntervalSchedule.objects.get_or_create(**interval_, defaults = interval_)
                data['interval'] = interval.id
            except:
                raise ValidationError('时间策略有误')
        if timetype == 'crontab' and crontab_:
            data['interval'] = None
            try:
                crontab_['timezone'] = 'Asia/Shanghai'
                crontab, _ = CrontabSchedule.objects.get_or_create(**crontab_, defaults = crontab_)
                data['crontab'] = crontab.id
            except:
                raise ValidationError('时间策略有误')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        data = request.data
        timetype = data.get('timetype', None)
        interval_ = data.get('interval_', None)
        crontab_ = data.get('crontab_', None)
        if timetype == 'interval' and interval_:
            data['crontab'] = None
            try:
                if 'id' in interval_:
                    del interval_['id']
                interval, _ = IntervalSchedule.objects.get_or_create(**interval_, defaults = interval_)
                data['interval'] = interval.id
            except:
                raise ValidationError('时间策略有误')
        if timetype == 'crontab' and crontab_:
            data['interval'] = None
            try:
                crontab_['timezone'] = 'Asia/Shanghai'
                if 'id'in crontab_:
                    del crontab_['id'] 
                crontab, _ = CrontabSchedule.objects.get_or_create(**crontab_, defaults = crontab_)
                data['crontab'] = crontab.id
            except:
                raise ValidationError('时间策略有误')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class DictTypeViewSet(ModelViewSet):
    """
    数据字典类型-增删改查
    """
    perms_map = {'get': '*', 'post': 'dicttype_create',
                 'put': 'dicttype_update', 'delete': 'dicttype_delete'}
    queryset = DictType.objects.all()
    serializer_class = DictTypeSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']


class DictViewSet(ModelViewSet):
    """
    数据字典-增删改查
    """
    perms_map = {'get': '*', 'post': 'dict_create',
                 'put': 'dict_update', 'delete': 'dict_delete'}
    # queryset = Dict.objects.get_queryset(all=True) # 获取全部的,包括软删除的
    queryset = Dict.objects.all()
    filterset_fields = ['type', 'is_used', 'type__code']
    serializer_class = DictSerializer
    search_fields = ['name']
    ordering_fields = ['sort']
    ordering = ['sort']

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        也可用utils.pageornot方法
        """
        if self.paginator is None:
            return None
        elif (not self.request.query_params.get('page', None)) and ((self.request.query_params.get('type__code', None)) or (self.request.query_params.get('type', None))):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

class PositionViewSet(ModelViewSet):
    """
    岗位-增删改查
    """
    perms_map = {'get': '*', 'post': 'position_create',
                 'put': 'position_update', 'delete': 'position_delete'}
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    pagination_class = None
    search_fields = ['name','description']
    ordering_fields = ['pk']
    ordering = ['pk']


class TestView(APIView):
    perms_map = {'get': 'test_view'}  # 单个API控权
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):
        return Response('测试api接口')


class PermissionViewSet(ModelViewSet):
    """
    权限-增删改查
    """
    perms_map = {'get': '*', 'post': 'perm_create',
                 'put': 'perm_update', 'delete': 'perm_delete'}
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['sort']
    ordering = ['pk']


class OrganizationViewSet(ModelViewSet):
    """
    组织机构-增删改查
    """
    perms_map = {'get': '*', 'post': 'org_create',
                 'put': 'org_update', 'delete': 'org_delete'}
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    pagination_class = None
    search_fields = ['name', 'type']
    ordering_fields = ['pk']
    ordering = ['pk']


class RoleViewSet(ModelViewSet):
    """
    角色-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']


class UserViewSet(ModelViewSet):
    """
    用户管理-增删改查
    """
    perms_map = {'get': '*', 'post': 'user_create',
                 'put': 'user_update', 'delete': 'user_delete'}
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filterset_class = UserFilter
    search_fields = ['username', 'name', 'phone', 'email']
    ordering_fields = ['-pk']

    def get_queryset(self):
        queryset = self.queryset
        if hasattr(self.get_serializer_class(), 'setup_eager_loading'):
            queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能优化
        dept = self.request.query_params.get('dept', None)  # 该部门及其子部门所有员工
        if dept:
            deptqueryset = get_child_queryset2(Organization.objects.get(pk=dept))
            queryset = queryset.filter(dept__in=deptqueryset)
        return queryset

    def get_serializer_class(self):
        # 根据请求类型动态变更serializer
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserModifySerializer

    def create(self, request, *args, **kwargs):
        # 创建用户默认添加密码
        password = request.data['password'] if 'password' in request.data else None
        if password:
            password = make_password(password)
        else:
            password = make_password('0000')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(password=password)
        return Response(serializer.data)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated], # perms_map={'put':'change_password'}
            url_name='change_password')
    def password(self, request, pk=None):
        """
        修改密码
        """
        user = request.user
        old_password = request.data['old_password']
        if check_password(old_password, user.password):
            new_password1 = request.data['new_password1']
            new_password2 = request.data['new_password2']
            if new_password1 == new_password2:
                user.set_password(new_password2)
                user.save()
                return Response('密码修改成功!', status=status.HTTP_200_OK)
            else:
                return Response('新密码两次输入不一致!', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('旧密码错误!', status=status.HTTP_400_BAD_REQUEST)

    # perms_map={'get':'*'}, 自定义action控权
    @action(methods=['get'], detail=False, url_name='my_info', permission_classes=[IsAuthenticated])
    def info(self, request, pk=None):
        """
        初始化用户信息
        """
        user = request.user
        perms = get_permission_list(user)
        data = {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'roles': user.roles.values_list('name', flat=True),
            'avatar': user.avatar,
            'perms': perms,
        }
        return Response(data)

class FileViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    文件上传用
    """
    perms_map = None
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filterset_fields = ['type']
    search_fields = ['name']
    ordering = ['-create_time']

    def perform_create(self, serializer):
        fileobj = self.request.data.get('file')
        name = fileobj._name
        size = fileobj.size
        mime = fileobj.content_type
        type = '其它'
        if 'image' in mime:
            type = '图片'
        elif 'video' in mime:
            type = '视频'
        elif 'audio' in mime:
            type = '音频'
        elif 'application' or 'text' in mime:
            type = '文档'
        instance = serializer.save(create_by = self.request.user, name=name, size=size, type=type, mime=mime)
        instance.path = settings.MEDIA_URL + instance.file.name
        instance.save()
