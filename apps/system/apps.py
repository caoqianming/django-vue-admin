from django.apps import AppConfig
from django.core.cache import cache


class SystemConfig(AppConfig):
    name = 'apps.system'
    verbose_name = '系统管理'

    def ready(self) -> None:
        # 启动时重新加载系统配置json
        if cache.get('cache_sysconfig_need_task', True):
            from server.settings import get_sysconfig
            get_sysconfig(reload=True)
            cache.set('cache_sysconfig_need_task', False, timeout=30)
        return super().ready()
