import traceback

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
import logging
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback
import json
from apps.utils.tasks import send_mail_task
from django.conf import settings


# 实例化myLogger
myLogger = logging.getLogger('log')


def custom_exception_hander(exc, context):
    """
    自定义异常处理
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(exc.message)

    request_id = getattr(context['request'], 'request_id', None)
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait
        data = {'err_detail': exc.detail}
        if isinstance(exc.detail, dict):
            data['err_code'] = exc.default_code
            data['err_msg'] = json.dumps(exc.detail, ensure_ascii=False) if 'detail' not in exc.detail else exc.detail['detail']  # 取一部分方便前端alert
        elif isinstance(exc.detail, list):
            data['err_code'] = exc.default_code
            data['err_msg'] = json.dumps(exc.detail, ensure_ascii=False)
        else:
            data = {'err_msg': exc.detail, 'err_code': exc.get_codes()}

        set_rollback()
        data['request_id'] = request_id
        status = exc.status_code
        if status not in [401, 404]:
            status = 400
        return Response(data, status=status, headers=headers)
    args = (request_id, traceback.format_exc())
    err_detail = f"{args[0]}-{args[1]}"
    myLogger.error(err_detail)
    if settings.DEBUG is False:
        send_mail_task.delay(message=err_detail)  # 500邮件通知到开发人员
    return Response(data={'err_code': 'server_error', 'err_detail': err_detail if settings.DEBUG else None, 'err_msg': '服务器错误'}, status=500)
