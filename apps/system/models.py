from django.contrib.auth.models import UserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.utils.models import CommonADModel, CommonAModel, CommonBModel, BaseModel, SoftDeletableManagerMixin
from django_celery_beat.models import IntervalSchedule, CrontabSchedule


class DataFilter(models.IntegerChoices):
    ALL = 10, '全部'
    SAMELEVE_AND_BELOW = 30, '同级及以下'
    THISLEVEL_AND_BELOW = 40, '本级及以下'
    THISLEVEL = 50, '本级'
    MYSELF = 60, '仅本人'


class Permission(BaseModel):
    """
    功能权限:目录,菜单,按钮
    """
    PERM_TYPE_LIST = 10
    PERM_TYPE_MENU = 20
    PERM_TYPE_BUTTON = 30
    menu_type_choices = (
        (PERM_TYPE_LIST, '目录'),
        (PERM_TYPE_MENU, '菜单'),
        (PERM_TYPE_BUTTON, '按钮')
    )
    name = models.CharField('名称', max_length=30)
    type = models.PositiveSmallIntegerField('类型', choices=menu_type_choices, default=30)
    sort = models.PositiveSmallIntegerField('排序标记', default=1)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='父')
    codes = models.JSONField('权限标识', default=list, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '功能权限表'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Dept(CommonAModel):
    """
    部门
    """
    name = models.CharField('名称', max_length=60)
    type = models.CharField('类型', max_length=20, default='dept')
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='父')
    sort = models.PositiveSmallIntegerField('排序标记', default=1)
    third_info = models.JSONField('三方系统信息', default=dict)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        ordering = ['sort']

    def __str__(self):
        return self.name


class Role(CommonADModel):
    """
    角色
    """
    name = models.CharField('名称', max_length=32)
    code = models.CharField('角色标识', max_length=32, null=True, blank=True)
    perms = models.ManyToManyField(Permission, blank=True, verbose_name='功能权限', related_name='role_perms')
    description = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return self.name


class Post(CommonADModel):
    """
    职位/岗位
    """
    name = models.CharField('名称', max_length=32)
    code = models.CharField('岗位标识', max_length=32, null=True, blank=True)
    description = models.CharField('描述', max_length=50, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='父')
    min_hour = models.PositiveSmallIntegerField('最小在岗时间', default=0)
    max_hour = models.PositiveSmallIntegerField('最长在岗时间', default=12)

    class Meta:
        verbose_name = '职位/岗位'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.name


class PostRole(BaseModel):
    """
    岗位角色关系
    """
    data_range = models.PositiveSmallIntegerField('数据权限范围', choices=DataFilter.choices,
                                                  default=DataFilter.THISLEVEL_AND_BELOW)
    post = models.ForeignKey(Post, verbose_name='关联岗位', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, verbose_name='关联角色', on_delete=models.CASCADE)


class SoftDeletableUserManager(SoftDeletableManagerMixin, UserManager):
    pass


class User(AbstractUser, CommonBModel):
    """
    用户
    """
    type = models.CharField('账号类型', max_length=10, default='employee')
    name = models.CharField('姓名', max_length=20, null=True, blank=True)
    phone = models.CharField('手机号', max_length=11, null=True, blank=True)
    avatar = models.CharField(
        '头像', default='/media/default/avatar.png', max_length=100, null=True, blank=True)
    superior = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='上级主管')
    post = models.ForeignKey(Post, verbose_name='主要岗位', on_delete=models.SET_NULL,
                             null=True, blank=True)
    posts = models.ManyToManyField(Post, through='system.userpost', related_name='user_posts')
    depts = models.ManyToManyField(Dept, through='system.userpost')
    roles = models.ManyToManyField(Role, verbose_name='关联角色')

    # 关联账号
    secret = models.CharField('密钥', max_length=100, null=True, blank=True)
    wx_openid = models.CharField('微信公众号OpenId', max_length=100, null=True, blank=True)
    wx_nickname = models.CharField('微信昵称', max_length=100, null=True, blank=True)
    wx_headimg = models.CharField('微信头像', max_length=100, null=True, blank=True)
    wxmp_openid = models.CharField('微信小程序OpenId', max_length=100, null=True, blank=True)

    objects = SoftDeletableUserManager()

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.username


class UserPost(BaseModel):
    """
    用户岗位关系表
    """
    name = models.CharField('名称', max_length=20, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='up_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='up_post')
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, related_name='up_dept')
    sort = models.PositiveSmallIntegerField('排序', default=1)

    class Meta:
        verbose_name = '用户岗位关系表'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'create_time']
        unique_together = ('user', 'post', 'dept')


class DictType(CommonAModel):
    """
    数据字典类型
    """
    name = models.CharField('名称', max_length=30)
    code = models.CharField('标识', max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '字典类型'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.name


class Dictionary(CommonAModel):
    """
    数据字典
    """
    name = models.CharField('名称', max_length=60)
    value = models.CharField('值', max_length=10, null=True, blank=True)
    code = models.CharField('标识', max_length=30, null=True, blank=True)
    description = models.TextField('描述', blank=True, null=True)
    type = models.ForeignKey(
        DictType, on_delete=models.CASCADE, verbose_name='类型')
    sort = models.PositiveSmallIntegerField('排序', default=1)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='父')
    is_used = models.BooleanField('是否有效', default=True)

    class Meta:
        verbose_name = '字典'
        verbose_name_plural = verbose_name
        unique_together = ('name', 'is_used', 'type')
        ordering = ['sort']

    def __str__(self):
        return self.name


class File(CommonAModel):
    """
    文件存储表,业务表根据具体情况选择是否外键关联
    """
    FILE_TYPE_DOC = 10
    FILE_TYPE_VIDEO = 20
    FILE_TYPE_AUDIO = 30
    FILE_TYPE_PIC = 40
    FILE_TYPE_OTHER = 50
    name = models.CharField('名称', max_length=100, null=True, blank=True)
    size = models.IntegerField('文件大小', default=1, null=True, blank=True)
    file = models.FileField('文件', upload_to='%Y/%m/%d/')
    type_choices = (
        (FILE_TYPE_DOC, '文档'),
        (FILE_TYPE_VIDEO, '视频'),
        (FILE_TYPE_AUDIO, '音频'),
        (FILE_TYPE_PIC, '图片'),
        (FILE_TYPE_OTHER, '其它')
    )
    mime = models.CharField('文件格式', max_length=120, null=True, blank=True)
    type = models.CharField('文件类型', max_length=50, choices=type_choices, default='文档')
    path = models.CharField('地址', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = '文件库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class MySchedule(CommonAModel):
    """
    常用周期
    """
    MS_TYPE = (
        (10, '间隔'),
        (20, '定时')
    )
    name = models.CharField('名称', max_length=200)
    type = models.PositiveSmallIntegerField('周期类型', default=10)
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.PROTECT, null=True, blank=True)
    crontab = models.ForeignKey(CrontabSchedule, on_delete=models.PROTECT, null=True, blank=True)