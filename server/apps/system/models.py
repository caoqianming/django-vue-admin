from django.db import models
from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone
from django.db.models.query import QuerySet

from utils.model import SoftModel, BaseModel
from simple_history.models import HistoricalRecords



class Position(BaseModel):
    """
    职位/岗位
    """
    name = models.CharField('名称', max_length=32, unique=True)
    description = models.CharField('描述', max_length=50, blank=True, null=True)

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
    parent = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')
    method = models.CharField('方法/代号', max_length=50,
                              unique=True, null=True, blank=True)

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
    parent = models.ForeignKey('self', null=True, blank=True,
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
        ('自定义', '自定义'),
        ('同级及以下', '同级及以下'),
        ('本级及以下', '本级及以下'),
        ('本级', '本级'),
        ('仅本人', '仅本人')
    )
    name = models.CharField('角色', max_length=32, unique=True)
    perms = models.ManyToManyField(Permission, blank=True, verbose_name='功能权限')
    datas = models.CharField('数据权限', max_length=50,
                             choices=data_type_choices, default='本级及以下')
    depts = models.ManyToManyField(
        Organization, blank=True, verbose_name='权限范围')
    description = models.CharField('描述', max_length=50, blank=True, null=True)

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
    phone = models.CharField('手机号', max_length=11,
                             null=True, blank=True, unique=True)
    avatar = models.CharField(
        '头像', default='/media/default/avatar.png', max_length=100, null=True, blank=True)
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

class DictType(SoftModel):
    """
    数据字典类型
    """
    name = models.CharField('名称', max_length=30)
    code = models.CharField('代号', unique=True, max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '字典类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Dict(SoftModel):
    """
    数据字典
    """
    name = models.CharField('名称', max_length=60)
    code = models.CharField('编号', max_length=30, null=True, blank=True)
    description = models.TextField('描述', blank=True, null=True)
    type = models.ForeignKey(
        DictType, on_delete=models.CASCADE, verbose_name='类型')
    sort = models.IntegerField('排序', default=1)
    parent = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')
    is_used = models.BooleanField('是否有效', default=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = '字典'
        verbose_name_plural = verbose_name
        unique_together = ('name', 'is_used', 'type')

    def __str__(self):
        return self.name

class CommonAModel(SoftModel):
    """
    业务用基本表A,包含create_by, update_by字段
    """
    create_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='创建人', related_name= '%(class)s_create_by')
    update_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='最后编辑人', related_name= '%(class)s_update_by')

    class Meta:
        abstract = True

class CommonBModel(SoftModel):
    """
    业务用基本表B,包含create_by, update_by, belong_dept字段
    """
    create_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='创建人', related_name = '%(class)s_create_by')
    update_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='最后编辑人', related_name = '%(class)s_update_by')
    belong_dept = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属部门', related_name= '%(class)s_belong_dept')

    class Meta:
        abstract = True


class File(CommonAModel):
    """
    文件存储表,业务表根据具体情况选择是否外键关联
    """
    name = models.CharField('名称', max_length=100, null=True, blank=True)
    size = models.IntegerField('文件大小', default=1, null=True, blank=True)
    file = models.FileField('文件', upload_to='%Y/%m/%d/')
    type_choices = (
        ('文档', '文档'),
        ('视频', '视频'),
        ('音频', '音频'),
        ('图片', '图片'),
        ('其它', '其它')
    )
    mime = models.CharField('文件格式', max_length=120, null=True, blank=True)
    type = models.CharField('文件类型', max_length=50, choices=type_choices, default='文档')
    path = models.CharField('地址', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = '文件库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name