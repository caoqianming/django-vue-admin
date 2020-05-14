from django.db import models
from django.apps import apps


def get_child_queryset_x(checkQueryset, fatherQueryset, noneQueryset, hasParent=True):
    '''
    获取所有子集
    查checkQueryset
    父fatherQueryset
    空noneQueryset
    是否包含父默认True
    '''
    if fatherQueryset is None:
        return noneQueryset
    if hasParent:
        noneQueryset = noneQueryset | fatherQueryset
    child_queryset = checkQueryset.filter(pid=fatherQueryset.first())
    while child_queryset:
        noneQueryset = noneQueryset | child_queryset
        child_queryset = checkQueryset.filter(pid__in=child_queryset)
    return noneQueryset.distinct()


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
        child_queryset = cls.objects.filter(pid=fatherQueryset.first())
        while child_queryset:
            queryset = queryset | child_queryset
            child_queryset = cls.objects.filter(pid__in=child_queryset)
    return queryset
