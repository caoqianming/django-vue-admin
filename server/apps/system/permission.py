from django.core.cache import cache
from rest_framework.permissions import BasePermission

from .models import Permission


def get_permission_list(user):
    """
    获取权限列表,可用redis存取
    """
    if user.is_superuser:
        perms_list = ['admin']
    else:
        perms = Permission.objects.none()
        roles = user.roles.all()
        if roles:
            for i in roles:
                perms = perms | i.perms.all()
        perms_list = perms.values_list('method', flat=True)
        perms_list = list(set(perms_list))
    cache.set(user.username, perms_list)
    cache.persist(user.username)
    return perms_list


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
        perms = cache.get(request.user)
        if not perms:
            perms = get_permission_list(request.user)
        if perms:
            if 'admin' in perms:
                return True
            elif not hasattr(view, 'perms_map'):
                return True
            else:
                perms_map = view.perms_map
                _method = request._request.method.lower()
                if perms_map:
                    for i in perms_map:
                        if (i[_method] or i['*']) in perms:
                            return True
                return False
        else:
            return False
