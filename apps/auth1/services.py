from django.core.cache import cache
from rest_framework.exceptions import ParseError
import re


def check_phone_code(phone, code, raise_exception=True):
    code_exist = cache.get(phone, None)
    if code_exist == code:
        return True
    if raise_exception:
        raise ParseError('验证码错误')
    return False



def validate_password(password):
    # 正则表达式匹配规则
    pattern = r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@#$%^&+=!])(?!.*\s).{8,}$"
    
    # 使用正则表达式进行匹配
    if re.match(pattern, password):
        return True
    else:
        return False
