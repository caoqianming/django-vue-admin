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


class WxmpClient:
    """
    微信小程序相关
    """

    def __init__(self, app_id=settings.WXMP_APPID,
                 app_secret=settings.WXMP_APPSECRET) -> None:
        self.app_id, self.app_secret = None, None
        if settings.WXMP_ENABLED:
            self.app_id = app_id
            self.app_secret = app_secret
            self.log = {}

    def request(self, url: str, method: str, params=dict(), json=dict(), timeout=10,
                file_path_rela=None, raise_exception=True):
        if not settings.WX_ENABLED:
            raise ParseError('微信小程序未启用')
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
            myLogger.error('微信小程序错误', exc_info=True)
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
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        _, res = self.request('/sns/jscode2session', params=params, method='get')
        return res


wxmpClient = WxmpClient()
