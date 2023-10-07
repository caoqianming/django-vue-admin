import uuid
from django.db import models


class DrfRequestLog(models.Model):
    """Logs Django rest framework API requests"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        'system.user',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    requested_at = models.DateTimeField(db_index=True)
    response_ms = models.PositiveIntegerField(default=0)
    path = models.CharField(
        max_length=400,
        db_index=True,
        help_text="请求地址",
    )
    view = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        db_index=True,
        help_text="执行视图",
    )
    view_method = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_index=True,
    )
    remote_addr = models.GenericIPAddressField()
    host = models.URLField()
    method = models.CharField(max_length=10)
    query_params = models.JSONField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    response = models.JSONField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)
    agent = models.TextField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "DRF请求日志"

    def __str__(self):
        return "{} {}".format(self.method, self.path)


class Tlog(models.Model):
    """第三方请求与处理日志
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    target = models.CharField('请求目标', max_length=20)
    result = models.CharField('请求结果', max_length=20)
    path = models.CharField(max_length=400, help_text="请求地址")
    params = models.JSONField(null=True, blank=True)
    body = models.JSONField(null=True, blank=True)
    method = models.CharField(max_length=10)
    requested_at = models.DateTimeField()
    response_ms = models.PositiveIntegerField(default=0)
    headers = models.JSONField(null=True, blank=True)
    response = models.JSONField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)