from django.db.models.signals import m2m_changed
from .models import Role, Permission, User
from django.dispatch import receiver
from django.core.cache import cache
from apps.utils.permission import get_user_perms_map

# 变更用户角色时动态更新权限或者前端刷新
# @receiver(m2m_changed, sender=User.roles.through)
# def update_perms_cache_user(sender, instance, action, **kwargs):
#     if action in ['post_remove', 'post_add']:
#         if cache.get('perms_' + instance.id, None):
#             get_user_perms_map(instance)