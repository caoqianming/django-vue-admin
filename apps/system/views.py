import configparser
import os
import importlib
import json
from drf_yasg import openapi
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django_celery_beat.models import (CrontabSchedule, IntervalSchedule,
                                       PeriodicTask)
from django_celery_results.models import TaskResult
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError, PermissionDenied
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.parsers import (JSONParser,
                                    MultiPartParser)
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.system.errors import OLD_PASSWORD_WRONG, PASSWORD_NOT_SAME, SCHEDULE_WRONG
from apps.system.filters import DeptFilterSet, UserFilterSet
# from django_q.models import Task as QTask, Schedule as QSchedule
from apps.utils.mixins import (CustomCreateModelMixin, MyLoggingMixin)
from django.conf import settings
from apps.utils.permission import ALL_PERMS, get_user_perms_map
from apps.utils.viewsets import CustomGenericViewSet, CustomModelViewSet
from server.celery import app as celery_app
from .models import (Dept, Dictionary, DictType, File, Permission, Post, PostRole, Role, User,
                     UserPost, MySchedule)
from .serializers import (ApkSerializer, DeptCreateUpdateSerializer, DeptSerializer, DictCreateUpdateSerializer,
                          DictSerializer, DictTypeCreateUpdateSerializer, DictTypeSerializer,
                          FileSerializer, PasswordChangeSerializer, PermissionCreateUpdateSerializer,
                          PermissionSerializer, PostCreateUpdateSerializer, PostRoleCreateSerializer,
                          PostRoleSerializer, PostSerializer,
                          PTaskSerializer, PTaskCreateUpdateSerializer, PTaskResultSerializer,
                          RoleCreateUpdateSerializer, RoleSerializer, TaskRunSerializer,
                          UserCreateSerializer, UserListSerializer, UserPostCreateSerializer,
                          UserPostSerializer, UserUpdateSerializer, MyScheduleCreateSerializer, MyScheduleSerializer)
from rest_framework.viewsets import GenericViewSet
from cron_descriptor import get_description
import locale
from drf_yasg.utils import swagger_auto_schema
from server.settings import get_sysconfig, update_sysconfig, update_dict

# logger.info('请求成功！ response_code:{}；response_headers:{}；
# response_body:{}'.format(response_code, response_headers, response_body[:251]))
# logger.error('请求出错-{}'.format(error))


class TaskList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取注册任务列表

        获取注册任务列表
        """
        tasks = list(
            sorted(name for name in celery_app.tasks if not name.startswith('celery.')))
        return Response(tasks)


# class QScheduleViewSet(CustomModelViewSet):
#     """
#     list:定时任务列表

#     定时任务列表

#     retrieve:定时任务详情

#     定时任务详情
#     """
#     queryset = QSchedule.objects.all()
#     serializer_class = QScheduleSerializer
#     search_fields = ['name', 'func']
#     filterset_fields = ['schedule_type']
#     ordering = ['-pk']

#     @action(methods=['get'], detail=True, perms_map={'post': 'qschedule:run_once'})
#     def run_once(self, request, pk=None):
#         """同步执行一次

#         同步执行一次
#         """
#         obj = self.get_object()
#         module, func = obj.func.rsplit(".", 1)
#         m = importlib.import_module(module)
#         f = getattr(m, func)
#         f(*obj.args.split(','), **eval(f"dict({obj.kwargs})"))
#         return Response()


# class QTaskResultViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
#     """
#     list:任务执行结果列表

#     任务执行结果列表

#     retrieve:任务执行结果详情

#     任务执行结果详情
#     """
#     perms_map = {'get': '*'}
#     filterset_fields = ['func']
#     queryset = QTask.objects.all()
#     serializer_class = QTaskResultSerializer
#     ordering = ['-started']
#     lookup_field = 'id'

class PTaskViewSet(CustomModelViewSet):
    """
    list:定时任务列表

    定时任务列表

    retrieve:定时任务详情

    定时任务详情
    """
    queryset = PeriodicTask.objects.exclude(name__contains='celery.')
    serializer_class = PTaskSerializer
    create_serializer_class = PTaskCreateUpdateSerializer
    update_serializer_class = PTaskCreateUpdateSerializer
    partial_update_serializer_class = PTaskCreateUpdateSerializer
    search_fields = ['name', 'task']
    filterset_fields = ['enabled']
    select_related_fields = ['interval', 'crontab']
    ordering = ['-id']

    @action(methods=['post'], detail=True, perms_map={'get': 'qtask.run_once'},
            serializer_class=TaskRunSerializer)
    def run_once(self, request, pk=None):
        """执行一次

        执行一次
        """
        obj = self.get_object()
        module, func = obj.task.rsplit(".", 1)
        m = importlib.import_module(module)
        f = getattr(m, func)
        if request.data.get('sync', True):
            f(*json.loads(obj.args), **json.loads(obj.kwargs))
            return Response()
        else:
            task_obj = f.delay(*json.loads(obj.args), **json.loads(obj.kwargs))
            return Response({'task_id': task_obj.id})

    @action(methods=['put'], detail=True, perms_map={'put': 'ptask.update'})
    def toggle(self, request, pk=None):
        """修改启用禁用状态

        修改启用禁用状态
        """
        obj = self.get_object()
        obj.enabled = False if obj.enabled else True
        obj.save()
        return Response()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """创建定时任务

        创建定时任务
        """
        data = request.data
        timetype = data.get('timetype', None)
        interval_ = data.get('interval_', None)
        crontab_ = data.get('crontab_', None)
        if timetype == 'interval' and interval_:
            data['crontab'] = None
            try:
                interval, _ = IntervalSchedule.objects.get_or_create(
                    **interval_, defaults=interval_)
                data['interval'] = interval.id
            except Exception:
                raise ParseError(**SCHEDULE_WRONG)
        if timetype == 'crontab' and crontab_:
            data['interval'] = None
            try:
                crontab_['timezone'] = 'Asia/Shanghai'
                crontab, _ = CrontabSchedule.objects.get_or_create(
                    **crontab_, defaults=crontab_)
                data['crontab'] = crontab.id
            except Exception:
                raise ParseError(**SCHEDULE_WRONG)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """更新定时任务

        更新定时任务
        """
        data = request.data
        timetype = data.get('timetype', None)
        interval_ = data.get('interval_', None)
        crontab_ = data.get('crontab_', None)
        if timetype == 'interval' and interval_:
            data['crontab'] = None
            try:
                if 'id' in interval_:
                    del interval_['id']
                interval, _ = IntervalSchedule.objects.get_or_create(
                    **interval_, defaults=interval_)
                data['interval'] = interval.id
            except Exception:
                raise ParseError(**SCHEDULE_WRONG)
        if timetype == 'crontab' and crontab_:
            data['interval'] = None
            try:
                crontab_['timezone'] = 'Asia/Shanghai'
                if 'id' in crontab_:
                    del crontab_['id']
                crontab, _ = CrontabSchedule.objects.get_or_create(
                    **crontab_, defaults=crontab_)
                data['crontab'] = crontab.id
            except Exception:
                raise ParseError(**SCHEDULE_WRONG)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()


class PTaskResultViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    """
    list:任务执行结果列表

    任务执行结果列表

    retrieve:任务执行结果详情

    任务执行结果详情
    """
    perms_map = {'get': '*'}
    filterset_fields = ['task_name', 'periodic_task_name', 'status']
    queryset = TaskResult.objects.all()
    serializer_class = PTaskResultSerializer
    ordering = ['-date_created']
    lookup_field = 'task_id'


class DictTypeViewSet(CustomModelViewSet):
    """数据字典类型-增删改查

    数据字典类型-增删改查
    """
    queryset = DictType.objects.all()
    serializer_class = DictTypeSerializer
    create_serializer_class = DictTypeCreateUpdateSerializer
    update_serializer_class = DictTypeCreateUpdateSerializer
    partial_update_serializer_class = DictTypeCreateUpdateSerializer
    search_fields = ['name']


class DictViewSet(CustomModelViewSet):
    """数据字典-增删改查

    数据字典-增删改查
    """
    # queryset = Dictionary.objects.get_queryset(all=True) # 获取全部的,包括软删除的
    queryset = Dictionary.objects.all()
    filterset_fields = ['type', 'is_used', 'type__code']
    serializer_class = DictSerializer
    create_serializer_class = DictCreateUpdateSerializer
    update_serializer_class = DictCreateUpdateSerializer
    partial_update_serializer_class = DictCreateUpdateSerializer
    search_fields = ['name']
    ordering = ['sort', 'create_time']


class PostViewSet(CustomModelViewSet):
    """岗位-增删改查

    岗位-增删改查
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    create_serializer_class = PostCreateUpdateSerializer
    update_serializer_class = PostCreateUpdateSerializer
    partial_update_serializer_class = PostCreateUpdateSerializer
    search_fields = ['name', 'code', 'description']
    ordering = ['create_time']


class PermissionViewSet(CustomModelViewSet):
    """菜单权限-增删改查

    菜单权限-增删改查
    """
    queryset = Permission.objects.all()
    filterset_fields = ['type']
    serializer_class = PermissionSerializer
    create_serializer_class = PermissionCreateUpdateSerializer
    update_serializer_class = PermissionCreateUpdateSerializer
    partial_update_serializer_class = PermissionCreateUpdateSerializer
    search_fields = ['name', 'codes']
    ordering = ['sort', 'create_time']

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def codes(self, request, pk=None):
        """获取全部权限标识

        需要先请求一次swagger
        """
        ALL_PERMS.sort()
        return Response(ALL_PERMS)


class DeptViewSet(CustomModelViewSet):
    """部门-增删改查

    部门-增删改查
    """
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    create_serializer_class = DeptCreateUpdateSerializer
    update_serializer_class = DeptCreateUpdateSerializer
    partial_update_serializer_class = DeptCreateUpdateSerializer
    filterset_class = DeptFilterSet
    search_fields = ['name']
    ordering = ['type', 'sort', 'create_time']

    # def filter_queryset(self, queryset):
    #     if not self.detail:
    #         self.request.query_params._mutable = True
    #         self.request.query_params.setdefault('type', 'dept')
    #     return super().filter_queryset(queryset)

    # def get_queryset(self):
    #     type = self.request.query_params.get('type', None)
    #     if type:
    #         queryset = Dept.objects.filter(type='rparty')
    #     else:
    #         queryset = Dept.objects.filter(type__in=['dept', 'company'])
    #     return queryset


class RoleViewSet(CustomModelViewSet):
    """角色-增删改查

    角色-增删改查
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    create_serializer_class = RoleCreateUpdateSerializer
    update_serializer_class = RoleCreateUpdateSerializer
    partial_update_serializer_class = RoleCreateUpdateSerializer
    search_fields = ['name', 'code']
    ordering = ['create_time']


class PostRoleViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin, CustomGenericViewSet):
    """岗位/角色关系

    岗位/角色关系
    """
    perms_map = {'get': '*', 'post': 'post.update', 'delete': 'post.update'}
    queryset = PostRole.objects.select_related('post', 'role').all()
    serializer_class = PostRoleSerializer
    create_serializer_class = PostRoleCreateSerializer
    filterset_fields = ['post', 'role']


class UserPostViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin, CustomGenericViewSet):
    """用户/岗位关系

    用户/岗位关系
    """
    perms_map = {'get': '*', 'post': 'user.update', 'delete': 'user.update'}
    queryset = UserPost.objects.select_related('user', 'post', 'dept').all()
    serializer_class = UserPostSerializer
    create_serializer_class = UserPostCreateSerializer
    filterset_fields = ['user', 'post', 'dept']
    ordering = ['sort', 'create_time']

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            user = instance.user
            up = UserPost.objects.filter(user=user).order_by(
                'sort', 'create_time').first()
            if up:
                user.belong_dept = up.dept
                user.post = up.post
                user.update_by = self.request.user
                user.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            user = instance.user
            instance.delete()
            up = UserPost.objects.filter(user=user).order_by(
                'sort', 'create_time').first()
            if up:
                user.belong_dept = up.dept
                user.post = up.post
            else:
                user.belong_dept = None
                user.post = None
            user.update_by = self.request.user
            user.save()


class UserViewSet(CustomModelViewSet):
    queryset = User.objects.get_queryset(all=True)
    serializer_class = UserListSerializer
    create_serializer_class = UserCreateSerializer
    update_serializer_class = UserUpdateSerializer
    filterset_class = UserFilterSet
    search_fields = ['username', 'name', 'phone', 'email', 'id']
    select_related_fields = ['superior', 'belong_dept', 'post']
    prefetch_related_fields = ['posts', 'roles', 'depts']
    ordering = ['create_time', 'type']

    def get_queryset(self):
        if self.request.method == 'GET' and (not self.request.query_params.get('is_deleted', None)):
            self.queryset = User.objects.all()
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        """创建用户

        创建用户
        """
        password = make_password('abc!0000')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(password=password, belong_dept=None)
        return Response(data=serializer.data)

    @action(methods=['put'], detail=False,
            permission_classes=[IsAuthenticated],
            serializer_class=PasswordChangeSerializer)
    def password(self, request, pk=None):
        """修改密码

        修改密码
        """
        user = request.user
        old_password = request.data['old_password']
        if check_password(old_password, user.password):
            new_password1 = request.data['new_password1']
            new_password2 = request.data['new_password2']
            if new_password1 == new_password2:
                if new_password1 == old_password:
                    raise ParseError('新密码不得与旧密码相同')
                user.set_password(new_password2)
                user.save()
                return Response()
            else:
                raise ParseError(**PASSWORD_NOT_SAME)
        else:
            raise ValidationError(**OLD_PASSWORD_WRONG)

    @action(methods=['post'], detail=True, perms_map={'post': '*'}, serializer_class=Serializer)
    def reset_password(self, request, pk=None):
        user = self.get_object()
        if request.user.is_superuser:
            user.set_password('abc!0000')
            user.save()
        else:
            raise PermissionDenied()
        return Response()

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def info(self, request, pk=None):
        """登录用户信息

        获取登录用户信息
        """
        user = request.user
        perms = get_user_perms_map(user)
        data = {
            'id': user.id,
            'username': user.username,
            'type': user.type,
            'name': user.name,
            'roles': user.roles.values_list('name', flat=True),
            'avatar': user.avatar,
            'perms': perms,
            'belong_dept': user.belong_dept.id if user.belong_dept else None,
            'post': user.post.id if user.post else None,
            'belong_dept_name': user.belong_dept.name if user.belong_dept else '',
            'post_name': user.post.name if user.post else '',
            'is_superuser': user.is_superuser,
            'wxmp_openid': user.wxmp_openid,
            'wx_openid': user.wx_openid
        }
        return Response(data)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def bind_wxmp(self, request, pk=None):
        """
        绑定微信小程序

        绑定微信小程序
        """
        openid = request.data['openid']
        if openid:
            user = request.user
            if user.wxmp_openid != openid:
                User.objects.filter(wxmp_openid=openid).update(
                    wxmp_openid=None)
                user.wxmp_openid = openid
                user.save()
        return Response({'wxmp_openid': openid})

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def unbind_wxmp(self, request, pk=None):
        """
        解绑微信小程序

        解绑微信小程序
        """
        user = request.user
        user.wxmp_openid = None
        user.save()
        return Response()

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def bind_wx(self, request, pk=None):
        """绑定微信公众号

        绑定微信公众号, 用于发送通知
        """
        openid = request.data['openid']
        if openid:
            user = request.user
            if user.wx_openid != openid:
                User.objects.filter(wx_openid=openid).update(wx_openid=None)
                user.wx_openid = openid
                user.save()
        return Response({'wx_openid': openid})

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def bind_secret(self, request, pk=None):
        """创建密钥

        创建密钥
        """
        secret = request.data['secret']
        if secret:
            user = request.user
            user.secret = secret
            user.save()
        return Response()


class FileViewSet(CustomCreateModelMixin, RetrieveModelMixin, ListModelMixin, CustomGenericViewSet):
    """文件上传

    list:
    文件列表

    文件列表

    create:
    文件上传

    文件上传
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filterset_fields = ['type']
    search_fields = ['name']
    cache_seconds = 0

    def perform_create(self, serializer):
        file_obj = self.request.data.get('file')
        name = file_obj._name
        size = file_obj.size
        mime = file_obj.content_type
        file_type = File.FILE_TYPE_OTHER
        if 'image' in mime:
            file_type = File.FILE_TYPE_PIC
        elif 'video' in mime:
            file_type = File.FILE_TYPE_VIDEO
        elif 'audio' in mime:
            file_type = File.FILE_TYPE_AUDIO
        elif 'application' or 'text' in mime:
            file_type = File.FILE_TYPE_DOC
        instance = serializer.save(
            create_by=self.request.user, name=name, size=size, type=file_type, mime=mime)
        instance.path = settings.MEDIA_URL + instance.file.name
        instance.save()


class ApkViewSet(MyLoggingMixin, ListModelMixin, CreateModelMixin, GenericViewSet):
    perms_map = {'get': '*', 'post': 'apk.upload'}
    serializer_class = ApkSerializer

    def get_authenticators(self):
        if self.request.method == 'GET':
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """
        获取apk信息

        获取apk信息
        """
        config = get_sysconfig()
        return Response({'version': config['apk']['apk_version'], 'file': config['apk']['apk_file']})

    def create(self, request, *args, **kwargs):
        """
        上传apk

        上传apk
        """
        sr = ApkSerializer(data=request.data)
        sr.is_valid(raise_exception=True)
        vdata = sr.validated_data
        update_sysconfig({
            "apk": {
                "apk_version": vdata['version'],
                "apk_file": vdata['file']
            }
        })
        return Response()


class MyScheduleViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, CustomGenericViewSet):
    perms_map = {'get': '*', 'post': '*',
                 'delete': 'myschedule.delete'}
    serializer_class = MyScheduleSerializer
    create_serializer_class = MyScheduleCreateSerializer
    queryset = MySchedule.objects.all()
    select_related_fields = ['interval', 'crontab']
    period_dict = {
        "days": "天",
        "hours": "小时",
        "minutes": "分钟",
        "seconds": "秒",
        "microseconds": "微秒"
    }

    def get_chinese_description(self, type: str = 'interval', data: dict = {}):
        """转换为汉语描述
        """
        print(data)
        if type == 'interval':
            return f"每隔{data['every']}{self.period_dict[data['period']]}"
        elif type == 'crontab':
            locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
            return get_description(f"{data['minute']} {data['hour']} {data['day_of_month']} {data['month_of_year']} {data['day_of_week']}")
        return ''

    @transaction.atomic
    def perform_create(self, serializer):
        vdata = serializer.validated_data
        vdata['create_by'] = self.request.user  # 不可少
        interval_data = vdata.pop('interval_', None)
        crontab_data = vdata.pop('crontab_', None)
        if vdata['type'] == 10:
            interval, _ = IntervalSchedule.objects.get_or_create(
                **interval_data, defaults=interval_data)
            obj = MySchedule(**vdata)
            obj.name = self.get_chinese_description('interval', interval_data)
            obj.interval = interval
            obj.save()
        elif vdata['type'] == 20:
            crontab_data['timezone'] = 'Asia/Shanghai'
            crontab, _ = CrontabSchedule.objects.get_or_create(
                **crontab_data, defaults=crontab_data)
            obj = MySchedule(**vdata)
            obj.name = self.get_chinese_description('crontab', crontab_data)
            obj.crontab = crontab
            obj.save()


class SysBaseConfigView(APIView):
    authentication_classes = []
    permission_classes = []
    read_keys = ['base', 'apk']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name="project_code", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=False)
    ])
    def get(self, request, format=None):
        """
        获取系统基本信息

        获取系统基本信息
        """
        project_code = request.query_params.get('project_code', '')
        if project_code:
            from apps.develop.models import Project
            try:
                project = Project.objects.get(code=project_code)
                config = project.config_json
            except Project.DoesNotExist:
                raise ParseError('项目不存在')
        else:
            config = get_sysconfig()
        base_dict = {key: config[key]
                     for key in self.read_keys if key in config}
        return Response(base_dict)


class SysConfigView(MyLoggingMixin, APIView):
    perms_map = {'get': 'sysconfig.view', 'put': 'sysconfig.update'}

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name="project_code", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_STRING, required=False),
        openapi.Parameter(name="reload", in_=openapi.IN_QUERY,
                          type=openapi.TYPE_BOOLEAN, required=False),
    ])
    def get(self, request, format=None):
        """
        获取config json

        获取config json
        """
        reload = False
        if request.query_params.get('reload', None):
            reload = True
        project_code = request.query_params.get('project_code', '')
        if project_code:
            from apps.develop.models import Project
            try:
                project = Project.objects.get(code=project_code)
                config = project.config_json
            except Project.DoesNotExist:
                raise ParseError('项目不存在')
        else:
            config = get_sysconfig(reload=reload)
        return Response(config)

    @swagger_auto_schema(request_body=Serializer)
    def put(self, request, format=None):
        """
        修改config json

        修改config json
        """
        data = request.data
        project_code = data.get('project_code', '')
        if project_code:
            from apps.develop.models import Project
            try:
                project = Project.objects.get(code=project_code)
                config = project.config_json
                update_dict(config, data)
                project.config_json = config
                project.save()
            except Project.DoesNotExist:
                raise ParseError('项目不存在')
        else:
            update_sysconfig(data)
        return Response()
