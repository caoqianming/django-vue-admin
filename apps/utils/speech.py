from aip import AipSpeech
from django.conf import settings
import uuid
import os
from django.utils import timezone


def generate_voice(msg: str, per: int = 0):
    """文本生成语音

    Args:
        msg (str): 文本
        per (int): 男/女声

    Returns:
        bool: 成功
        str: 地址
        dict: result
    """
    client = AipSpeech(settings.BD_SP_ID, settings.BD_SP_KEY, settings.BD_SP_SECRET)
    result = client.synthesis(msg, 'zh', 1, {'vol': 5, 'spd': 5, 'per': per})
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        file_name = '{}.mp3'.format(uuid.uuid4())
        path = '/media/' + timezone.now().strftime('%Y/%m/%d/')
        full_path = settings.BASE_DIR + path
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        with open(full_path + file_name, 'wb') as f:
            f.write(result)
            return True, path + file_name, None
    return False, None, result
