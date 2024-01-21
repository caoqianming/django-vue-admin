# 基本配置
SECRET_KEY = 'xxxxxx'
BASE_PROJECT_CODE = 'xxxxxx'  # 一旦配置不要轻易改变
BASE_URL = 'http://127.0.0.1:8000'
BASE_URL_IN = 'http://127.0.0.1:8000'
BASE_URL_OUT = 'http://127.0.0.1:8000'

# 邮箱配置
EMAIL_HOST = 'xx'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'xx'
EMAIL_HOST_PASSWORD = 'xx'
EMAIL_USE_TLS = True


# 数据库配置
CACHE_LOCATION = "redis://127.0.0.1:6379/2"
CELERY_BROKER_URL = "redis://127.0.0.1:6379/3"
CELERY_TASK_DEFAULT_QUEUE = BASE_PROJECT_CODE
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'xxx',
        'USER': 'xx',
        'PASSWORD': 'xx',
        'HOST': 'xx',
        'PORT': 'xx',
    }
}

# 雪花ID
SNOW_DATACENTER_ID = 1

# 百度语音
BD_SP_ID = 'xx'
BD_SP_KEY = 'xx'
BD_SP_SECRET = 'xx'

# 运维相关
SD_PWD = 'xx'
BACKUP_PATH = '/home/xx/xx/xx'
SH_PATH = '/home/xx/xx/xx/sh'

# 微信相关
WXMP_ENABLED = False
WXMP_APPID = 'xx'
WXMP_APPSECRET = 'xx'

WX_ENABLED = False
WX_APPID = 'xx'  # 测试号
WX_APPSECRET = 'xx'
