from django.db.models.signals import m2m_changed
from .models import Role, Permission, User
from django.dispatch import receiver
from django.core.cache import cache
from .permission import get_permission_list

# 变更用户角色时动态更新权限或者前端刷新
@receiver(m2m_changed, sender=User.roles.through)
def update_perms_cache_user(sender, instance, action, **kwargs):
    if action in ['post_remove', 'post_add']:
        if cache.get(instance.username+'__perms', None):
            get_permission_list(instance)