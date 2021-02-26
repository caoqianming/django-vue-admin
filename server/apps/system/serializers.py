import re

from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
from rest_framework import serializers

from .models import (Dict, DictType, File, Organization, Permission, Position,
                     Role, User)

class IntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'

class CrontabSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ['timezone']

class PTaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = ['name', 'task', 'interval', 'crontab', 'args', 'kwargs']

class PTaskSerializer(serializers.ModelSerializer):
    interval_ = IntervalSerializer(source='interval', read_only=True)
    crontab_ = CrontabSerializer(source='crontab', read_only=True)
    schedule = serializers.SerializerMethodField()
    timetype = serializers.SerializerMethodField()
    class Meta:
        model = PeriodicTask
        fields = '__all__'
    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('interval','crontab')
        return queryset
    
    def get_schedule(self, obj):
        if obj.interval:
            return obj.interval.__str__()
        if obj.crontab:
            return obj.crontab.__str__()
        return ''
    
    def get_timetype(self, obj):
        if obj.interval:
            return 'interval'
        if obj.crontab:
            return 'crontab'
        return 'interval'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"

class DictTypeSerializer(serializers.ModelSerializer):
    """
    数据字典类型序列化
    """
    class Meta:
        model = DictType
        fields = '__all__'


class DictSerializer(serializers.ModelSerializer):
    """
    数据字典序列化
    """
    class Meta:
        model = Dict
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    """
    岗位序列化
    """
    class Meta:
        model = Position
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """
    class Meta:
        model = Role
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    """
    权限序列化
    """
    class Meta:
        model = Permission
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    """
    组织架构序列化
    """
    type = serializers.ChoiceField(
        choices=Organization.organization_type_choices, default='部门')

    class Meta:
        model = Organization
        fields = '__all__'


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化
    """
    dept_name = serializers.StringRelatedField(source='dept')
    roles_name = serializers.StringRelatedField(source='roles', many=True)
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email', 'position',
                  'username', 'is_active', 'date_joined', 'dept_name', 'dept', 'roles', 'avatar', 'roles_name']

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('superior','dept')
        queryset = queryset.prefetch_related('roles',)
        return queryset

class UserModifySerializer(serializers.ModelSerializer):
    """
    用户编辑序列化
    """
    phone = serializers.CharField(max_length=11, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'email', 'dept',
                  'position', 'avatar', 'is_active', 'roles', 'is_superuser']

    def validate_phone(self, phone):
        re_phone = '^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
        if not re.match(re_phone, phone):
            raise serializers.ValidationError('手机号码不合法')
        return phone


class UserCreateSerializer(serializers.ModelSerializer):
    """
    创建用户序列化
    """
    username = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=11, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'email', 'dept',
                  'position', 'avatar', 'is_active', 'roles', 'is_superuser']

    def validate_username(self, username):
        if User.objects.filter(username=username):
            raise serializers.ValidationError(username + ' 账号已存在')
        return username

    def validate_phone(self, phone):
        re_phone = '^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
        if not re.match(re_phone, phone):
            raise serializers.ValidationError('手机号码不合法')
        if User.objects.filter(phone=phone):
            raise serializers.ValidationError('手机号已经被注册')
        return phone
