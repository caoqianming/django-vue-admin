import logging
from functools import wraps
from apps.utils.tasks import send_mail_task
import traceback
import json
from django.core.cache import cache
from rest_framework.exceptions import ParseError

myLogger = logging.getLogger('log')


def auto_log(name='', raise_exception=True, send_mail=False):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                real_func = func(*args, **kwargs)
                return real_func
            except Exception:
                myLogger.error(name, exc_info=True)
                if send_mail:
                    send_mail_task.delay(message=traceback.format_exc())
                if raise_exception:
                    raise
        return wrapper
    return decorate


def idempotent(seconds=4):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rdata = args[1].data
            rdata['request_userid'] = getattr(args[1], 'user').id
            rdata['request_path'] = getattr(args[1], 'path')
            hash_k = hash(json.dumps(rdata))
            hash_v_e = cache.get(hash_k, None)
            if hash_v_e is None:
                cache.set(hash_k, 'o', seconds)
                real_func = func(*args, **kwargs)
                # real_func.render()
                # cache.set(hash_k, real_func, seconds)
                return real_func
            elif hash_v_e == 'o':  # 说明请求正在处理
                raise ParseError(f'请求忽略,请{seconds}秒后重试')
        return wrapper
    return decorate