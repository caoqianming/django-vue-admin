# from __future__ import absolute_import, unicode_literals
from celery import Task
from celery import shared_task
import logging
from django.conf import settings
from server.settings import get_sysconfig
import importlib
from django.core.cache import cache

# 实例化myLogger
myLogger = logging.getLogger('log')

@shared_task
def send_mail_task(**args):
    config = get_sysconfig()
    subject = args.get('subject', '500')
    args['subject'] = '{}:{}_{}_{}'.format(
        settings.SYS_NAME, settings.SYS_VERSION, config['base']['base_name_short'], subject)
    args['from_email'] = args.get('from_email', settings.EMAIL_HOST_USER)
    args['recipient_list'] = args.get(
        'recipient_list',  settings.EMAIL_DEVELOPERS if hasattr(settings, 'EMAIL_DEVELOPERS') else [settings.EMAIL_HOST_USER])
    cache_key = f'error_mail_{subject}'
    email_tuple = cache.get(cache_key)
    if email_tuple is None:
        email_tuple = (0, True)
        cache.set(cache_key, email_tuple, 60)
    email_count, email_enable = email_tuple
    if email_enable:
        email_count += 1
        if email_count > 4:
            email_enable = False
            # 如果频率高于每分钟4封,则自动屏蔽半小时
            cache.set(cache_key, (email_count, email_enable), 1800)
            args['subject'] = args['subject'] + '_发送频繁'
        else:
            cache.set(cache_key, (email_count, True), 60)
        from django.core.mail import send_mail
        send_mail(**args)

class CustomTask(Task):
    """
    自定义的任务回调
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        detail ='Task {0} raised exception: {1!r}\n{2!r}'.format(
                    task_id, exc, einfo.traceback)
        myLogger.error(detail)
        send_mail_task.delay(subject=f'task_error_{self.name}', message=detail)
        return super().on_failure(exc, task_id, args, kwargs, einfo)

@shared_task(base=CustomTask)
def ctask_run(func_str: str, *args, **kwargs):
    """通用celery函数/将普通函数转为celery执行/也可直接运行
    """
    module, func = func_str.rsplit(".", 1)
    m = importlib.import_module(module)
    f = getattr(m, func)
    f(*args, **kwargs)