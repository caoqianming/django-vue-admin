from django.core.cache import cache
import time
from threading import Thread
import uuid

import requests
from django.conf import settings
from rest_framework.exceptions import APIException, ParseError
import logging
from apps.ops.models import Tlog
from apps.utils.errors import WX_REQUEST_ERROR
from apps.utils.tools import print_roundtrip
from django.utils.timezone import now
import traceback
requests.packages.urllib3.disable_warnings()
# 实例化myLogger
myLogger = logging.getLogger('log')


class WxClient:
    """
    微信公众号相关
    """

    def __init__(self, app_id=settings.WX_APPID,
                 app_secret=settings.WX_APPSECRET) -> None:
        if settings.WX_ENABLED:
            self.app_id = app_id
            self.app_secret = app_secret
            self.isRuning = True
            self.token = None  # 普通token
            self.t = None  # 线程
            self.log = {}
            self.setup()

    def _get_token_loop(self):
        while self.isRuning:
            parmas = {
                'grant_type': 'client_credential',
                'appid': self.app_id,
                'secret': self.app_secret
            }
            _, ret = self.request(url='/cgi-bin/token', params=parmas, method='get')
            self.token = ret['access_token']
            cache.set(self.app_id + '_token', self.token, timeout=3600)
            time.sleep(3000)

    def setup(self):
        t = Thread(target=self._get_token_loop, args=(), daemon=True)
        t.start()

    def __del__(self):
        """
        自定义销毁
        """
        self.isRuning = False
        # self.t.join()

    def request(self, url: str, method: str, params=dict(), json=dict(), timeout=10,
                file_path_rela=None, raise_exception=True):
        if not settings.WX_ENABLED:
            raise ParseError('微信公众号未启用')
        self.log = {"requested_at": now(), "id": uuid.uuid4(), "path": url, "method": method,
                    "params": params, "body": json, "target": "wx", "result": 10}
        files = None
        if file_path_rela:  # 相对路径
            files = {'file': open(settings.BASE_DIR + file_path_rela, 'rb')}
        try:
            if params:
                url = url.format(**params)
                self.log.update({"path": url})
            r = getattr(requests, method)('{}{}'.format('https://api.weixin.qq.com', url),
                                          params=params, json=json,
                                          timeout=timeout, files=files, verify=False)
        except Exception:
            errors = traceback.format_exc()
            myLogger.error('微信错误', exc_info=True)
            self.handle_log(result='error', errors=errors)
            if raise_exception:
                raise APIException(**WX_REQUEST_ERROR)
            return 'error', WX_REQUEST_ERROR
        # if settings.DEBUG:
        #     print_roundtrip(r)
        if r.status_code == 200:
            ret = r.json()
            if 'errcode' in ret and ret['errcode'] not in [0, '0']:
                detail = '微信错误:' + \
                    '{}|{}'.format(str(ret['errcode']), ret.get('errmsg', ''))
                err_detail = dict(detail=detail, code='wx_'+str(ret['errcode']))
                self.handle_log(result='fail', response=ret)
                if raise_exception:
                    raise ParseError(**err_detail)
                return 'fail', dict(detail=detail, code='wx_'+str(ret['errcode']))
            # self.handle_log(result='success', response=ret)  # 成功的日志就不记录了
            return 'success', ret

        self.handle_log(result='error', response=None)
        if raise_exception:
            raise APIException(**WX_REQUEST_ERROR)
        return 'error', WX_REQUEST_ERROR

    def _get_response_ms(self):
        """
        Get the duration of the request response cycle is milliseconds.
        In case of negative duration 0 is returned.
        """
        response_timedelta = now() - self.log["requested_at"]
        response_ms = int(response_timedelta.total_seconds() * 1000)
        return max(response_ms, 0)

    def handle_log(self, result, response=None, errors=None):
        self.log.update({
            "result": result,
            "response": response,
            "response_ms": self._get_response_ms(),
            "errors": errors
        })
        Tlog(**self.log).save()

    def get_basic_info(self, code):
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        _, res = self.request('/sns/oauth2/access_token', params=params, method='get')
        return res

    def send_tem_msg(self, data: dict):
        """发送模板消息
        """

        _, res = self.request('/cgi-bin/message/template/send',
                              params={'access_token': self.token}, json=data, method='post')
        return res


wxClient = WxClient()
