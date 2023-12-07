import time
import django.utils.timezone as timezone
from django.db import models
from django.db.models import Model
from django.db.models.query import QuerySet
from apps.utils.snowflake import idWorker
from django.db import IntegrityError

# 自定义软删除查询基类


class SoftDeletableQuerySetMixin(object):
    '''
    QuerySet for SoftDeletableModel. Instead of removing instance sets
    its ``is_deleted`` field to True.
    '''

    def delete(self, soft=True):
        '''
        Soft delete objects from queryset (set their ``is_deleted``
        field to True)
        '''
        if soft:
            self.update(is_deleted=True)
        else:
            return super(SoftDeletableQuerySetMixin, self).delete()


class SoftDeletableQuerySet(SoftDeletableQuerySetMixin, QuerySet):
    pass


class SoftDeletableManagerMixin(object):
    '''
    Manager that limits the queryset by default to show only not deleted
    instances of model.
    '''
    _queryset_class = SoftDeletableQuerySet

    def get_queryset(self, all=False):
        '''
        Return queryset limited to not deleted entries.
        '''
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints
        if all:
            return self._queryset_class(**kwargs)
        return self._queryset_class(**kwargs).filter(is_deleted=False)


class SoftDeletableManager(SoftDeletableManagerMixin, models.Manager):
    pass


class BaseModel(models.Model):
    """
    基本表
    """
    id = models.CharField(max_length=20, primary_key=True,
                          editable=False, verbose_name='主键ID', help_text='主键ID')
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(
        auto_now=True, verbose_name='修改时间', help_text='修改时间')
    is_deleted = models.BooleanField(
        default=False, verbose_name='删除标记', help_text='删除标记')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        # 出现了雪花ID重复, 先这样异常处理一下;已经修改了snowflake, 以防万一, 这里依然保留
        gen_id = False
        if not self.id:
            gen_id = True
            self.id = idWorker.get_id()
        try:
            return super().save(*args, **kwargs)
        except IntegrityError as e:
            if gen_id:
                time.sleep(0.01)
                self.id = idWorker.get_id()
                return super().save(*args, **kwargs)
            raise e


class SoftModel(BaseModel):
    """
    软删除基本表
    """
    class Meta:
        abstract = True

    objects = SoftDeletableManager()

    def delete(self, using=None, soft=True, update_by=None, *args, **kwargs):
        '''
        这里需要真删除的话soft=False即可
        '''
        if soft:
            self.is_deleted = True
            self.update_by = update_by
            self.save(using=using)
        else:

            return super(SoftModel, self).delete(using=using, *args, **kwargs)


class CommonAModel(SoftModel):
    """
    业务用基本表A,包含create_by, update_by字段
    """
    create_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='创建人', related_name='%(class)s_create_by')
    update_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='最后编辑人', related_name='%(class)s_update_by')
    # delete_by = models.ForeignKey(
    #     'system.user', null=True, blank=True, on_delete=models.SET_NULL,
    #     verbose_name='删除人', related_name='%(class)s_delete_by')

    class Meta:
        abstract = True


class CommonBModel(SoftModel):
    """
    业务用基本表B,包含create_by, update_by, belong_dept字段
    """
    create_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='创建人', related_name='%(class)s_create_by')
    update_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='最后编辑人', related_name='%(class)s_update_by')
    # delete_by = models.ForeignKey(
    #     'system.user', null=True, blank=True, on_delete=models.SET_NULL,
    #     verbose_name='删除人', related_name='%(class)s_delete_by')
    belong_dept = models.ForeignKey(
        'system.dept', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='所属部门', related_name='%(class)s_belong_dept')

    class Meta:
        abstract = True


class CommonADModel(BaseModel):
    """
    业务用基本表A, 物理删除, 包含create_by, update_by字段
    """
    create_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='创建人', related_name='%(class)s_create_by')
    update_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='最后编辑人', related_name='%(class)s_update_by')
    # delete_by = models.ForeignKey(
    #     'system.user', null=True, blank=True, on_delete=models.SET_NULL,
    #     verbose_name='删除人', related_name='%(class)s_delete_by')

    class Meta:
        abstract = True


class CommonBDModel(BaseModel):
    """
    业务用基本表B, 物理删除, 包含create_by, update_by, belong_dept字段
    """
    create_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='创建人', related_name='%(class)s_create_by')
    update_by = models.ForeignKey(
        'system.user', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='最后编辑人', related_name='%(class)s_update_by')
    # delete_by = models.ForeignKey(
    #     'system.user', null=True, blank=True, on_delete=models.SET_NULL,
    #     verbose_name='删除人', related_name='%(class)s_delete_by')
    belong_dept = models.ForeignKey(
        'system.dept', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name='所属部门', related_name='%(class)s_belong_dept')

    class Meta:
        abstract = True


def get_model_info(cls_or_instance):
    """
    返回类似 system.dept 的字符
    """
    if isinstance(cls_or_instance, Model):
        # 是一个模型实例
        app_label = cls_or_instance._meta.app_label
        model_name = cls_or_instance._meta.model_name
    else:
        # 假定是一个模型类
        app_label = cls_or_instance._meta.app_label
        model_name = cls_or_instance._meta.model_name

    return f'{app_label}.{model_name}'
