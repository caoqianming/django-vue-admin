# from __future__ import absolute_import, unicode_literals
from celery import Task
from celery import shared_task
import logging
from django.conf import settings
from server.settings import get_sysconfig

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
        detail = '{0!r} failed: {1!r}'.format(task_id, exc)
        myLogger.error(detail)
        send_mail_task.delay(subject='task_error', message=detail)
        return super().on_failure(exc, task_id, args, kwargs, einfo)
