from django.core.cache import cache
from rest_framework.permissions import BasePermission
from apps.utils.queryset import get_child_queryset2
from apps.system.models import DataFilter, Dept, Permission, PostRole, UserPost, User
from django.db.models.query import QuerySet
from typing import List

ALL_PERMS = [

]


def get_user_perms_map(user):
    """
    获取权限字典,可用redis存取(包括功能和数据权限)
    """
    user_perms_map = {}
    if user.is_superuser:
        for perm in Permission.objects.all():
            if perm.codes:
                for code in perm.codes:
                    user_perms_map[code] = {}
    else:
        objs = UserPost.objects.filter(user=user).exclude(post=None)
        for i in objs:
            dept_id = str(i.dept.id)
            for pr in PostRole.objects.filter(post=i.post):
                """
                岗位角色
                """
                for perm in Permission.objects.filter(role_perms=pr.role):
                    if perm.codes:
                        for code in perm.codes:
                            if code in user_perms_map:
                                data_range = user_perms_map[code].get(
                                    dept_id, -1)
                                if pr.data_range < data_range:
                                    user_perms_map[code][dept_id] = pr.data_range
                            else:
                                user_perms_map[code] = {dept_id: pr.data_range}
    cache.set('perms_' + str(user.id), user_perms_map, timeout=300)
    return user_perms_map


def has_perm(user: User, perm_codes: List[str]):
    """
    返回用户是否具有给定权限列表中的权限
    """
    user_perms_map = cache.get(f'perms_{user.id}', None)
    if user_perms_map is None:
        user_perms_map = get_user_perms_map(user)
    for item in perm_codes:
        if item in user_perms_map:
            return True
    return False


class RbacPermission(BasePermission):
    """
    基于角色的权限校验类
    """

    def has_permission(self, request, view):
        """
        权限校验逻辑
        :param request:
        :param view:
        :return:
        """
        if not hasattr(view, 'perms_map'):
            return True
        user_perms_map = cache.get('perms_' + request.user.id, None)
        if user_perms_map is None:
            user_perms_map = get_user_perms_map(request.user)
        if isinstance(user_perms_map, dict):
            perms_map = view.perms_map
            _method = request._request.method.lower()
            if perms_map:
                for key in perms_map:
                    if key == _method or key == '*':
                        if perms_map[key] in user_perms_map or perms_map[key] == '*':
                            return True
            return False
        return False


class RbacDataMixin:
    """
    数据权限控权返回的queryset
    在必须的View下继承
    需要控数据权限的表需有belong_dept, create_by, update_by字段(部门, 创建人, 编辑人)
    带性能优化
    此处对性能有较大影响,根据业务需求进行修改或取舍
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

        if hasattr(self.get_serializer_class(), 'setup_eager_loading'):
            queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能优化

        if self.request.user.is_superuser:
            return queryset

        if hasattr(queryset.model, 'belong_dept'):
            user = self.request.user
            user_perms_map = cache.get('perms_' + user.id, None)
            if user_perms_map is None:
                user_perms_map = get_user_perms_map(self.request.user)
            if isinstance(user_perms_map, dict):
                if hasattr(self.view, 'perms_map'):
                    perms_map = self.view.perms_map
                    action_str = perms_map.get(
                        self.request._request.method.lower(), None)
                    if '*' in perms_map:
                        return queryset
                    elif action_str == '*':
                        return queryset
                    elif action_str in user_perms_map:
                        new_queryset = queryset.none()
                        for dept_id, data_range in user_perms_map[action_str].items:
                            dept = Dept.objects.get(id=dept_id)
                            if data_range == DataFilter.ALL:
                                return queryset
                            elif data_range == DataFilter.SAMELEVE_AND_BELOW:
                                if dept.parent:
                                    belong_depts = get_child_queryset2(
                                        dept.parent)
                                else:
                                    belong_depts = get_child_queryset2(dept)
                                queryset = queryset.filter(
                                    belong_dept__in=belong_depts)
                            elif data_range == DataFilter.THISLEVEL_AND_BELOW:
                                belong_depts = get_child_queryset2(dept)
                                queryset = queryset.filter(
                                    belong_dept__in=belong_depts)
                            elif data_range == DataFilter.THISLEVEL:
                                queryset = queryset.filter(belong_dept=dept)
                            elif data_range == DataFilter.MYSELF:
                                queryset = queryset.filter(create_by=user)
                            new_queryset = new_queryset | queryset
                        return new_queryset
                    else:
                        return queryset.none()
        return queryset
