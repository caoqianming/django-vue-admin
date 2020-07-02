from django.db.models import Q
from django.db.models.query import QuerySet
from rest_framework.generics import GenericAPIView
from apps.system.mixins import CreateUpdateModelBMixin
from utils.queryset import get_child_queryset2


class RbacFilterSet(CreateUpdateModelBMixin, GenericAPIView):
    """
    数据权限控权返回的queryset
    在必须的View下继承
    需要控数据权限的表需有belong_dept, create_by, update_by字段(部门, 创建人, 编辑人)
    带性能优化
    包括必要的创建和编辑操作
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
        if hasattr(queryset.model, 'belong_dept'):
            user = self.request.user
            roles = user.roles
            data_range = roles.values_list('datas', flat=True)
            if '全部' in data_range:
                return queryset
            elif '自定义' in data_range:
                if roles.depts.exists():
                    queryset = queryset.filter(belong_dept__in = roles.depts)
                    return queryset
            elif '同级及以下' in data_range:
                if user.dept.parent:
                    belong_depts = get_child_queryset2(user.dept.parent)
                    queryset = queryset.filter(belong_dept__in = belong_depts)
                    return queryset
            elif '本级及以下' in data_range:
                belong_depts = get_child_queryset2(user.dept)
                queryset = queryset.filter(belong_dept__in = belong_depts)
                return queryset
            elif '本级' in data_range:
                queryset = queryset.filter(belong_dept = user.dept)
                return queryset
            elif '仅本人' in data_range:
                queryset = queryset.filter(Q(create_by=user)|Q(update_by=user))
                return queryset
        if hasattr(self.get_serializer_class(), 'setup_eager_loading'):
            queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能优化    
        return queryset


def rbac_filter_queryset(user, queryset):
    """
    数据权限控权返回的queryset方法
    需要控数据权限的表需有belong_dept, create_by, update_by字段(部门, 创建人, 编辑人)
    传入user实例,queryset
    """
    roles = user.roles
    data_range = roles.values_list('datas', flat=True)
    if hasattr(queryset.model, 'belong_dept'):
        if '全部' in data_range:
            return queryset
        elif '自定义' in data_range:
            if roles.depts.exists():
                queryset = queryset.filter(belong_dept__in = roles.depts)
                return queryset
        elif '同级及以下' in data_range:
            if user.dept.parent:
                belong_depts = get_child_queryset2(user.dept.parent)
                queryset = queryset.filter(belong_dept__in = belong_depts)
                return queryset
        elif '本级及以下' in data_range:
            belong_depts = get_child_queryset2(user.dept)
            queryset = queryset.filter(belong_dept__in = belong_depts)
            return queryset
        elif '本级' in data_range:
            queryset = queryset.filter(belong_dept = user.dept)
            return queryset
        elif '仅本人' in data_range:
            queryset = queryset.filter(Q(create_by=user)|Q(update_by=user))
            return queryset    
    return queryset

