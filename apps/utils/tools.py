import re
import textwrap
import random
import string
from datetime import datetime
from django.conf import settings
import base64
import requests
from io import BytesIO
from rest_framework.serializers import ValidationError

def is_close(num1, num2=0, tolerance=1e-9):
    """
    Check if a numeric value (int, float, etc.) is close.
    """
    if isinstance(num1, float) or isinstance(num2, float):     # Float check
        return abs(num1-num2) < tolerance
    elif isinstance(num1, int) and isinstance(num2, int):         # Integer check
        return num1 == num2
    else:
        raise ValueError("Unsupported numeric type")

def tran64(s):
    missing_padding = len(s) % 4
    if missing_padding != 0:
        s = s+'=' * (4 - missing_padding)
    return s


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


def print_roundtrip(response, *args, **kwargs):
    def format_headers(d): return '\n'.join(f'{k}: {v}' for k, v in d.items())
    print(textwrap.dedent('''
        ---------------- request ----------------
        {req.method} {req.url}
        {reqhdrs}

        {req.body}
        ---------------- response ----------------
        {res.status_code} {res.reason} {res.url}
        {reshdrs}

        {res.text}
    ''').format(
        req=response.request,
        res=response,
        reqhdrs=format_headers(response.request.headers),
        reshdrs=format_headers(response.headers),
    ))


def ranstr(num):
    salt = ''.join(random.sample(string.ascii_lowercase + string.digits, num))
    return salt


def rannum(num):
    salt = ''.join(random.sample(string.digits, num))
    return salt


def timestamp_to_time(millis):
    """10位时间戳转换为日期格式字符串"""
    return datetime.fromtimestamp(millis)


def convert_to_base64(path: str):
    """给定图片转base64

    Args:
        path (str): 图片地址
    """
    if path.startswith('http'):  # 如果是网络图片
        return str(base64.b64encode(BytesIO(requests.get(url=path).content).read()), 'utf-8')
    else:
        with open(settings.BASE_DIR + path, 'rb') as f:
            return str(base64.b64encode(f.read()), 'utf-8')


def p_in_poly(p, poly):
    px = p['x']
    py = p['y']
    flag = False

    i = 0
    l = len(poly)
    j = l - 1
    # for(i = 0, l = poly.length, j = l - 1; i < l; j = i, i++):
    while i < l:
        sx = poly[i]['x']
        sy = poly[i]['y']
        tx = poly[j]['x']
        ty = poly[j]['y']

        # 点与多边形顶点重合
        if (sx == px and sy == py) or (tx == px and ty == py):
            return (px, py)

        # 判断线段两端点是否在射线两侧
        if (sy < py and ty >= py) or (sy >= py and ty < py):
            # 线段上与射线 Y 坐标相同的点的 X 坐标
            x = sx + (py - sy) * (tx - sx) / (ty - sy)
            # 点在多边形的边上
            if x == px:
                return (px, py)
            # 射线穿过多边形的边界
            if x > px:
                flag = not flag
        j = i
        i += 1

    # 射线穿过多边形边界的次数为奇数时点在多边形内
    return (px, py) if flag else 'out'


def check_id_number_e(val):
    re_s = r'^[1-9]\d{5}(18|19|20|(3\d))\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$'
    if not re.match(re_s, val):
        raise ValidationError('身份证号校验错误')
    return val


def get_info_from_id(val):
    birth = val[6:14]
    birth_year = birth[0:4]
    age = datetime.now().year - int(birth_year)
    sex = int(val[-2])
    gender = '女'
    if sex % 2:
        gender = '男'
    return dict(age=age, gender=gender)


def check_id_number(idcard):
    """校验身份证号

    Args:
        id_number (_type_): 身份证号
    """
    Errors = ['身份证号码位数不对!', '身份证号码出生日期超出范围或含有非法字符!', '身份证号码校验错误!', '身份证地区非法!']
    area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
            "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北",
            "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
            "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}
    idcard = str(idcard)
    idcard = idcard.strip()
    idcard_list = list(idcard)

    # 地区校验
    if str(idcard[0:2]) not in area:
        return False, Errors[3]

    # 15位身份号码检测
    if len(idcard) == 15:
        if ((int(idcard[6:8]) + 1900) % 4 == 0 or (
                (int(idcard[6:8]) + 1900) % 100 == 0 and (int(idcard[6:8]) + 1900) % 4 == 0)):
            ereg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
        else:
            ereg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
        if re.match(ereg, idcard):
            return True, ''
        else:
            return False, Errors[1]
    # 18位身份号码检测
    elif len(idcard) == 18:
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if (int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10]) % 4 == 0)):
            # 闰年出生日期的合法性正则表达式
            ereg = re.compile(
                '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')
        else:
            # 平年出生日期的合法性正则表达式
            ereg = re.compile(
                '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')
        # 测试出生日期的合法性
        if re.match(ereg, idcard):
            # 计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 + (
                int(idcard_list[2]) + int(idcard_list[12])) * 10 + (
                int(idcard_list[3]) + int(idcard_list[13])) * 5 + (
                int(idcard_list[4]) + int(idcard_list[14])) * 8 + (
                int(idcard_list[5]) + int(idcard_list[15])) * 4 + (
                int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(
                idcard_list[8]) * 6 + int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10X98765432"
            M = JYM[Y]  # 判断校验位
            if M == idcard_list[17]:  # 检测ID的校验位
                return True, ''
            else:
                return False, Errors[2]
        else:
            return False, Errors[1]
    else:
        return False, Errors[0]


def check_phone_e(phone):
    re_phone = r'^1\d{10}$'
    if not re.match(re_phone, phone):
        raise ValidationError('手机号格式错误')
    return phone


def compare_dicts(dict1, dict2, ignore_order=False):
    if ignore_order:
        for key in sorted(dict1.keys()):
            if key not in dict2 or not compare_values(dict1[key], dict2[key], ignore_order):
                return False
        return True
    else:
        return dict1 == dict2


def compare_lists_of_dicts(list1, list2, ignore_order=False):
    """比较两个列表，这里的列表包含字典（对象）"""
    if ignore_order:
        # 转换列表中的字典为元组列表，然后排序进行比较
        sorted_list1 = sorted((tuple(sorted(d.items())) for d in list1))
        sorted_list2 = sorted((tuple(sorted(d.items())) for d in list2))
        return sorted_list1 == sorted_list2
    else:
        # 按顺序比较列表中的字典
        return all(compare_dicts(obj1, obj2) for obj1, obj2 in zip(list1, list2))


def compare_values(val1, val2, ignore_order=False):
    """通用比较函数，也可以处理字典和列表。"""
    if isinstance(val1, list) and isinstance(val2, list):
        # 假设这里我们关心列表中对象的顺序
        return compare_lists_of_dicts(val1, val2, ignore_order)
    elif isinstance(val1, dict) and isinstance(val2, dict):
        return compare_dicts(val1, val2, ignore_order)
    else:
        return val1 == val2
