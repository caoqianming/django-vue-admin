# from __future__ import absolute_import, unicode_literals
from celery import Task
from celery import shared_task
import logging
from django.conf import settings
from server.settings import get_sysconfig
import importlib

# 实例化myLogger
myLogger = logging.getLogger('log')


@shared_task
def send_mail_task(**args):
    config = get_sysconfig()
    from django.core.mail import send_mail
    args['subject'] = '{}:{}_{}_{}'.format(
        settings.SYS_NAME, settings.SYS_VERSION, config['base']['base_name_short'], args.get('subject', '500'))
    args['from_email'] = args.get('from_email', settings.EMAIL_HOST_USER)
    args['recipient_list'] = args.get(
        'recipient_list', [settings.EMAIL_HOST_USER])
    send_mail(**args)

class CustomTask(Task):
    """
    自定义的任务回调
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        detail ='Task {0} raised exception: {1!r}\n{2!r}'.format(
                    task_id, exc, einfo.traceback)
        myLogger.error(detail)
        send_mail_task.delay(subject='task_error', message=detail)
        return super().on_failure(exc, task_id, args, kwargs, einfo)

@shared_task(base=CustomTask)
def ctask_run(func_str: str, *args, **kwargs):
    """通用celery函数/将普通函数转为celery执行/也可直接运行
    """
    module, func = func_str.rsplit(".", 1)
    m = importlib.import_module(module)
    f = getattr(m, func)
    f(*args, **kwargs)