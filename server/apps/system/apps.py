from django.apps import AppConfig


class SystemConfig(AppConfig):
    name = 'apps.system'
    verbose_name = '系统管理'

    def ready(self):
        import apps.system.signals