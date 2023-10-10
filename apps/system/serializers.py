
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
from rest_framework import serializers
from django_celery_results.models import TaskResult
from apps.system.errors import USERNAME_EXIST
from apps.utils.fields import MyFilePathField
from apps.utils.serializers import CustomModelSerializer
from apps.utils.constants import EXCLUDE_FIELDS, EXCLUDE_FIELDS_BASE
from apps.utils.tools import check_phone_e
from .models import (Dictionary, DictType, File, Dept, MySchedule, Permission, Post, PostRole,
                     Role, User, UserPost)
from rest_framework.exceptions import ParseError, ValidationError
from django.db import transaction
from rest_framework.validators import UniqueValidator
from django.conf import settings
from django.db.models import Q
# from django_q.models import Task as QTask, Schedule as QSchedule


# class QScheduleSerializer(CustomModelSerializer):
#     success = serializers.SerializerMethodField()

#     class Meta:
#         model = QSchedule
#         fields = '__all__'

#     def get_success(self, obj):
#         return obj.success()


# class QTaskResultSerializer(CustomModelSerializer):
#     args = serializers.SerializerMethodField()
#     kwargs = serializers.SerializerMethodField()
#     result = serializers.SerializerMethodField()

#     class Meta:
#         model = QTask
#         fields = '__all__'

#     def get_args(self, obj):
#         return obj.args

#     def get_kwargs(self, obj):
#         return obj.kwargs

#     def get_result(self, obj):
#         return obj.result

class TaskRunSerializer(serializers.Serializer):
    sync = serializers.BooleanField(default=True)


class IntervalSerializer(CustomModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class CrontabSerializer(CustomModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ['timezone']


class PTaskCreateUpdateSerializer(CustomModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = ['name', 'task', 'interval', 'crontab', 'args', 'kwargs']


class PTaskSerializer(CustomModelSerializer):
    interval_ = IntervalSerializer(source='interval', read_only=True)
    crontab_ = CrontabSerializer(source='crontab', read_only=True)
    schedule = serializers.SerializerMethodField()
    timetype = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicTask
        fields = '__all__'

    def get_schedule(self, obj):
        if obj.interval:
            return obj.interval.__str__()
        elif obj.crontab:
            return obj.crontab.__str__()
        return ''

    def get_timetype(self, obj):
        if obj.interval:
            return 'interval'
        elif obj.crontab:
            return 'crontab'
        return 'interval'


class PTaskResultSerializer(CustomModelSerializer):
    class Meta:
        model = TaskResult
        fields = '__all__'


class FileSerializer(CustomModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class DictTypeSerializer(CustomModelSerializer):
    """
    数据字典类型序列化
    """

    class Meta:
        model = DictType
        fields = '__all__'


class DictTypeCreateUpdateSerializer(CustomModelSerializer):
    class Meta:
        model = DictType
        fields = ['name', 'code', 'parent']


class DictSerializer(CustomModelSerializer):
    """
    数据字典序列化
    """

    class Meta:
        model = Dictionary
        fields = '__all__'


class DictSimpleSerializer(CustomModelSerializer):
    class Meta:
        model = Dictionary
        fields = ['id', 'name', 'code']


class DictCreateUpdateSerializer(CustomModelSerializer):
    """
    数据字典序列化
    """

    class Meta:
        model = Dictionary
        exclude = EXCLUDE_FIELDS


class PostSerializer(CustomModelSerializer):
    """
    岗位序列化
    """

    class Meta:
        model = Post
        fields = '__all__'


class PostCreateUpdateSerializer(CustomModelSerializer):
    """
    岗位序列化
    """

    class Meta:
        model = Post
        exclude = EXCLUDE_FIELDS

    def create(self, validated_data):
        if Post.objects.filter(name=validated_data['name']).exists():
            raise ValidationError('该岗位已存在')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if Post.objects.filter(name=validated_data['name']).exclude(id=instance.id).exists():
            raise ValidationError('该岗位已存在')
        return super().update(instance, validated_data)


class PostSimpleSerializer(CustomModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'name', 'code']


class RoleSerializer(CustomModelSerializer):
    """
    角色序列化
    """

    class Meta:
        model = Role
        fields = '__all__'


class RoleSimpleSerializer(CustomModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'code']


class RoleCreateUpdateSerializer(CustomModelSerializer):
    """
    角色序列化
    """
    name = serializers.CharField(label="名称", validators=[
        UniqueValidator(queryset=Role.objects.all(), message='已存在相同名称的角色')])
    code = serializers.CharField(label="标识", validators=[
        UniqueValidator(queryset=Role.objects.all(), message='已存在相同标识的角色')])

    class Meta:
        model = Role
        exclude = EXCLUDE_FIELDS


class PermissionSerializer(serializers.ModelSerializer):
    """
    权限序列化
    """

    class Meta:
        model = Permission
        fields = '__all__'


class PermissionCreateUpdateSerializer(serializers.ModelSerializer):
    """
    权限序列化
    """

    class Meta:
        model = Permission
        exclude = EXCLUDE_FIELDS_BASE


class DeptSimpleSerializer(CustomModelSerializer):
    class Meta:
        model = Dept
        fields = ['id', 'name', 'type']


class DeptSerializer(CustomModelSerializer):
    """
    组织架构序列化
    """
    class Meta:
        model = Dept
        fields = '__all__'


class DeptCreateUpdateSerializer(CustomModelSerializer):
    """
    部门序列化
    """
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Dept.objects.all(), required=True)

    class Meta:
        model = Dept
        exclude = EXCLUDE_FIELDS + ['third_info']

    @transaction.atomic
    def create(self, validated_data):
        ins = super().create(validated_data)
        sync_dahua_dept(ins)
        return ins

    @transaction.atomic
    def update(self, instance, validated_data):
        ins = super().update(instance, validated_data)
        sync_dahua_dept(ins)
        return ins


class UserSimpleSerializer(CustomModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone']


class UserSignatureSerializer(CustomModelSerializer):
    signature = serializers.CharField(
        source='employee.signature', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'signature']


class UserListSerializer(CustomModelSerializer):
    """
    用户列表序列化
    """
    belong_dept_name = serializers.CharField(
        source='belong_dept.name', read_only=True)
    post_name = serializers.CharField(source='post.name', read_only=True)
    # posts_ = PostSimpleSerializer(source='posts', many=True)
    avatar_f = MyFilePathField(source='avatar', read_only=True)

    class Meta:
        model = User
        exclude = ['password', 'secret']


def phone_exist(phone):
    if User.objects.filter(phone=phone).exists():
        raise serializers.ValidationError(**PHONE_EXIST)


def user_exist(username):
    if User.objects.filter(username=username).exists():
        raise serializers.ValidationError(**USERNAME_EXIST)
    return username


class UserUpdateSerializer(CustomModelSerializer):
    """
    用户编辑序列化
    """
    phone = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'name', 'avatar', 'phone', 'type', 'is_deleted']

    def update(self, instance, validated_data):
        if User.objects.filter(username=validated_data['username']
                               ).exclude(id=instance.id).exists():
            raise ParseError(**USERNAME_EXIST)
        return super().update(instance, validated_data)


class UserCreateSerializer(CustomModelSerializer):
    """
    创建用户序列化
    """
    username = serializers.CharField(required=True, validators=[user_exist])
    phone = serializers.CharField(required=False, validators=[phone_exist])

    class Meta:
        model = User
        fields = ['username', 'name', 'avatar', 'phone', 'type']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(label="原密码")
    new_password1 = serializers.CharField(label="新密码1")
    new_password2 = serializers.CharField(label="新密码2")


class UserPostSerializer(CustomModelSerializer):
    """
    用户-岗位序列化
    """
    user_ = UserSimpleSerializer(source='user', read_only=True)
    post_ = PostSimpleSerializer(source='post', read_only=True)
    dept_ = DeptSimpleSerializer(source='dept', read_only=True)

    class Meta:
        model = UserPost
        fields = '__all__'


class UserPostCreateSerializer(CustomModelSerializer):
    class Meta:
        model = UserPost
        exclude = EXCLUDE_FIELDS_BASE

    def create(self, validated_data):
        return super().create(validated_data)


class PostRoleSerializer(CustomModelSerializer):
    """
    岗位-角色序列化
    """
    post_ = PostSimpleSerializer(source='post', read_only=True)
    role_ = RoleSimpleSerializer(source='role', read_only=True)

    class Meta:
        model = PostRole
        fields = '__all__'


class PostRoleCreateSerializer(CustomModelSerializer):
    """
    岗位-角色创建序列化
    """
    class Meta:
        model = PostRole
        fields = ['post', 'role', 'data_range']


class UserInfoSerializer(CustomModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'post',
                  'avatar', 'belong_dept', 'type']


class ApkSerializer(serializers.Serializer):
    version = serializers.CharField(label='版本号')
    file = serializers.CharField(label='文件地址')


class IntervalScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class CrontabScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ['timezone']


class MyScheduleCreateSerializer(CustomModelSerializer):
    interval_ = IntervalScheduleSerializer(allow_null=True, required=False)
    crontab_ = CrontabScheduleSerializer(allow_null=True, required=False)

    class Meta:
        model = MySchedule
        fields = ['type', 'interval_', 'crontab_']

    def validate(self, attrs):
        if attrs['type'] == 10 and attrs.get('interval_', None):
            pass
        elif attrs['type'] == 20 and attrs.get('crontab_', None):
            pass
        else:
            raise ValidationError('信息有误')
        return super().validate(attrs)


class MyScheduleSerializer(CustomModelSerializer):
    interval_ = IntervalScheduleSerializer(source='interval', read_only=True)
    crontab = CrontabScheduleSerializer(source='crontab', read_only=True)

    class Meta:
        model = MySchedule
        fields = '__all__'
