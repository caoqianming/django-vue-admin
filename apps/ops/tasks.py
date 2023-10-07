# Create your tasks here
from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from apps.ops.models import DrfRequestLog
from apps.utils.tasks import CustomTask
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import os

import subprocess
from server.settings import DATABASES, BACKUP_PATH, SH_PATH, SD_PWD


@shared_task
def backup_database():
    """
    备份数据库
    """
    import datetime
    name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    command = 'echo "{}" | sudo -S pg_dump "user={} password={} dbname={}" > {}/bak_{}.sql'.format(
        SD_PWD,
        DATABASES['default']['USER'],
        DATABASES['default']['PASSWORD'],
        DATABASES['default']['NAME'],
        BACKUP_PATH + '/database',
        name)
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)
    if completed.returncode != 0:
        return completed.stderr


@shared_task
def reload_server_git():
    command = 'bash {}/git_server.sh'.format(SH_PATH)
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)
    if completed.returncode != 0:
        return completed.stderr


@shared_task
def reload_web_git():
    command = 'bash {}/git_web.sh'.format(SH_PATH)
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)
    if completed.returncode != 0:
        return completed.stderr


@shared_task
def reload_server_only():
    command = 'echo "{}" | sudo -S supervisorctl reload'.format(SD_PWD)
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)
    return completed


@shared_task
def backup_media():
    command = 'bash {}/backup_media.sh'.format(SH_PATH)
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)
    if completed.returncode != 0:
        return completed.stderr


@shared_task(base=CustomTask)
def clear_drf_log(days: int = 7):
    """清除N天前的日志记录,默认七天

    清除N天前的日志记录
    """
    now = timezone.now()
    days7_ago = now - timedelta(days=days)
    DrfRequestLog.objects.filter(create_time__lte=days7_ago).delete()


@shared_task(base=CustomTask)
def clear_dbbackup(num: int = 7):
    """
    清除N条前的数据库备份记录,默认七条

    清除N条前的数据库备份记录
    """
    from apps.ops.views import get_file_list
    backpath = settings.BACKUP_PATH + '/database'
    files = get_file_list(backpath)
    files_remove_list = files[num:]
    for f in files_remove_list:
        filepath = os.path.join(backpath, f)
        os.remove(filepath)
