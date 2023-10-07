# Create your tasks here
from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from apps.utils.tasks import CustomTask
from celery import shared_task
from django_celery_results.models import TaskResult
from django.utils import timezone


@shared_task(base=CustomTask)
def cleanup_dcr():
    """清空三十日前的定时任务执行记录

    清空三十日前的定时任务执行记录
    """
    now = timezone.now()
    days30_ago = now - timedelta(days=30)
    TaskResult.objects.filter(periodic_task_name__isnull=False, date_done__lte=days30_ago).delete()
