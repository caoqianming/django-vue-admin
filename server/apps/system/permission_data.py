from django.db.models import Q
from django.db.models.query import QuerySet
from rest_framework.generics import GenericAPIView

from utils.queryset import get_child_queryset2


class RbacFilterSet(GenericAPIView):
    """
    数据权限控权返回的queryset
    在必须的View下继承
    需要控数据权限的表需有belong_to, create_by, update_by字段(部门, 创建人, 编辑人)
    """
    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        if hasattr(queryset.model, 'belong_to'):
            user = self.request.user
            roles = user.roles
            data_range = roles.values_list('datas', flat=True)
            if '全部' in data_range:
                return queryset
            elif '自定义' in data_range:
                if roles.depts.exists():
                    queryset = queryset.filter(belong_to__in = roles.depts)
                    return queryset
            elif '同级及以下' in data_range:
                if user.dept.pid:
                    belong_tos = get_child_queryset2(user.dept.pid)
                    queryset = queryset.filter(belong_to__in = belong_tos)
                    return queryset
            elif '本级及以下' in data_range:
                belong_tos = get_child_queryset2(user.dept)
                queryset = queryset.filter(belong_to__in = belong_tos)
                return queryset
            elif '本级' in data_range:
                queryset = queryset.filter(belong_to = user.dept)
                return queryset
            elif '仅本人' in data_range:
                queryset = queryset.filter(Q(create_by=user)|Q(update_by=user))
                return queryset
            
        return queryset


def rbac_filter_queryset(user, queryset):
    """
    数据权限控权返回的queryset方法
    需要控数据权限的表需有belong_to, create_by, update_by字段(部门, 创建人, 编辑人)
    传入user实例,queryset
    """
    roles = user.roles
    data_range = roles.values_list('datas', flat=True)
    if '全部' in data_range:
        return queryset
    elif '自定义' in data_range:
        if roles.depts.exists():
            queryset = queryset.filter(belong_to__in = roles.depts)
            return queryset
    elif '同级及以下' in data_range:
        if user.dept.pid:
            belong_tos = get_child_queryset2(user.dept.pid)
            queryset = queryset.filter(belong_to__in = belong_tos)
            return queryset
    elif '本级及以下' in data_range:
        belong_tos = get_child_queryset2(user.dept)
        queryset = queryset.filter(belong_to__in = belong_tos)
        return queryset
    elif '本级' in data_range:
        queryset = queryset.filter(belong_to = user.dept)
        return queryset
    elif '仅本人' in data_range:
        queryset = queryset.filter(Q(create_by=user)|Q(update_by=user))
        return queryset    
    return queryset

