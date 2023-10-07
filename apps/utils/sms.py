from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import logging
from server.settings import get_sysconfig
from apps.utils.decorators import auto_log

# 实例化myLogger
myLogger = logging.getLogger('log')

@auto_log(name='阿里云短信', raise_exception=True, send_mail=True)
def send_sms(phone: str, template_code: int, template_param: dict):
    config = get_sysconfig()
    if config['sms'].get('enabled', True) is False:
        return
    client = AcsClient(config['sms']['xn_key'], config['sms']['xn_secret'], 'default')
    request = CommonRequest()
    # 固定json
    request.set_accept_format('json')
    # 固定地址
    request.set_domain('sms11.hzgxr.com:40081')
    # 固定POST
    request.set_method('POST')
    # 固定HTTP
    request.set_protocol_type('http')  # https | http
    # 固定版本号
    request.set_version('2017-05-25')
    # 固定操作名
    request.set_action_name('SendSms')
    # 手机号码
    request.add_query_param('PhoneNumbers', phone)
    # 签名名称
    request.add_query_param('SignName', config['sms']['xn_sign'])
    # 模板CODE
    request.add_query_param('TemplateCode', template_code)
    # 如果有模板参数 填写模板参数 如果无 无须填写
    request.add_query_param('TemplateParam', json.dumps(template_param))
    res = client.do_action(request)
    res_dict = json.loads(str(res, encoding='utf-8'))
    # print(phone, template_code, template_param, res_dict)
    if res_dict['result'] == 0:

        return True, res_dict
    else:
        myLogger.error("短信发送失败:{}-{}-{}-{}".format(phone, template_code, str(template_param), str(res_dict)))
        return False, res_dict


def send_sms_huawei():
    """华为短信发送/备用
    """


def send_sms_tencent():
    """腾讯短信发送/备用
    """