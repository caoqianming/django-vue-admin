from django.db import models
from django.apps import apps


def get_child_queryset_u(checkQueryset, obj, hasParent=True):
    '''
    获取所有子集
    查的范围checkQueryset
    父obj
    是否包含父默认True
    '''
    cls = type(obj)
    queryset = cls.objects.none()
    fatherQueryset = cls.objects.filter(pk=obj.id)
    if hasParent:
        queryset = queryset | fatherQueryset
    child_queryset = checkQueryset.filter(parent=obj)
    while child_queryset:
        queryset = queryset | child_queryset
        child_queryset = checkQueryset.filter(parent__in=child_queryset)
    return queryset


def get_child_queryset(name, pk, hasParent=True):
    '''
    获取所有子集
    app.model名称
    Id
    是否包含父默认True
    '''
    app, model = name.split('.')
    cls = apps.get_model(app, model)
    queryset = cls.objects.none()
    fatherQueryset = cls.objects.filter(pk=pk)
    if fatherQueryset.exists():
        if hasParent:
            queryset = queryset | fatherQueryset
        child_queryset = cls.objects.filter(parent=fatherQueryset.first())
        while child_queryset:
            queryset = queryset | child_queryset
            child_queryset = cls.objects.filter(parent__in=child_queryset)
    return queryset

def get_child_queryset2(obj, hasParent=True):
    '''
    获取所有子集
    obj实例
    数据表需包含parent字段
    是否包含父默认True
    '''
    cls = type(obj)
    queryset = cls.objects.none()
    fatherQueryset = cls.objects.filter(pk=obj.id)
    if hasParent:
        queryset = queryset | fatherQueryset
    child_queryset = cls.objects.filter(parent=obj)
    while child_queryset:
        queryset = queryset | child_queryset
        child_queryset = cls.objects.filter(parent__in=child_queryset)
    return queryset