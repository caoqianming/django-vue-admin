from django.db import models
from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone
from django.db.models.query import QuerySet

from utils.model import SoftModel, BaseModel


class DictType(SoftModel):
    """
    数据字典类型
    """
    name = models.CharField('名称', max_length=30)
    code = models.CharField('代号', unique=True, max_length=30)
    pid = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')


class Dict(SoftModel):
    """
    数据字典
    """
    name = models.CharField('名称', max_length=30, unique=True)
    desc = models.TextField('描述', blank=True, null=True)
    type = models.ForeignKey(
        DictType, on_delete=models.CASCADE, verbose_name='类型')
    sort = models.IntegerField('排序', default=1)
    pid = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')


class Position(BaseModel):
    """
    职位/岗位
    """
    name = models.CharField('名称', max_length=32, unique=True)
    desc = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '职位/岗位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Permission(SoftModel):
    """
    功能权限:目录,菜单,接口
    """
    menu_type_choices = (
        ('目录', '目录'),
        ('菜单', '菜单'),
        ('接口', '接口')
    )
    name = models.CharField('名称', max_length=30)
    type = models.CharField('类型', max_length=20,
                            choices=menu_type_choices, default='接口')
    is_frame = models.BooleanField('外部链接', default=False)
    sort = models.IntegerField('排序标记', default=1)
    pid = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')
    method = models.CharField('方法/代号', max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '功能权限表'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Organization(SoftModel):
    """
    组织架构
    """
    organization_type_choices = (
        ('公司', '公司'),
        ('部门', '部门')
    )
    name = models.CharField('名称', max_length=60)
    type = models.CharField('类型', max_length=20,
                            choices=organization_type_choices, default='部门')
    pid = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '组织架构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Role(SoftModel):
    """
    角色
    """
    data_type_choices = (
        ('全部', '全部'),
        ('本级', '本级'),
        ('本级及以下', '本级及以下'),
        ('仅本人', '仅本人'),
        ('自定义', '自定义')
    )
    name = models.CharField('角色', max_length=32, unique=True)
    perms = models.ManyToManyField(Permission, blank=True, verbose_name='功能权限')
    datas = models.CharField('数据权限', max_length=50,
                             choices=data_type_choices, default='本级及以下')
    depts = models.ManyToManyField(
        Organization, blank=True, verbose_name='权限范围')
    desc = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    用户
    """
    name = models.CharField('姓名', max_length=20, null=True, blank=True)
    phone = models.CharField('手机号码', max_length=11,
                             null=True, blank=True, unique=True)
    avatar = models.CharField(
        '头像', default='/media/default/avatar.png', max_length=1000, null=True, blank=True)
    dept = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='组织')
    position = models.ManyToManyField(Position, blank=True, verbose_name='岗位')
    superior = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='上级主管')
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.username

class CommonModel(SoftModel):
    """
    业务用基本表
    """
    create_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='创建人', related_name='create_by')
    update_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='最后编辑人', related_name='update_by')

    class Meta:
        abstract = True