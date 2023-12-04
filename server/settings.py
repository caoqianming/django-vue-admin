"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from datetime import datetime, timedelta
import os
import json
import sys
from . import conf
from django.core.cache import cache
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SYS_JSON_PATH = os.path.join(BASE_DIR, 'server/conf.json')


def get_sysconfig(reload=False):
    config = cache.get('system_config', None)
    if config is None or reload:
        # 读取配置文件
        if not os.path.exists(SYS_JSON_PATH):
            raise SystemError('未找到配置文件')
        with open(SYS_JSON_PATH, 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            cache.set('system_config', config)
            return config
    return config


def update_dict(dict1, dict2):
    for key, value in dict2.items():
        if key == 'apk_file':  # apk_file拷贝到固定位置
            from shutil import copyfile
            copyfile(BASE_DIR + value, BASE_DIR + '/media/zc_ehs.apk')
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            update_dict(dict1[key], value)
        else:
            dict1[key] = value


def update_sysconfig(new_dict):
    config = get_sysconfig()
    update_dict(config, new_dict)
    with open(SYS_JSON_PATH, 'wb') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=False).encode('utf-8'))
    cache.set('system_config', config)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = conf.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = conf.DEBUG

ALLOWED_HOSTS = ['*']

SYS_NAME = 'HAPPY-DRF'
SYS_VERSION = '2.2.2'


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',
    'drf_yasg',
    'rest_framework',
    'django_filters',
    'apps.utils',
    'apps.system',
    'apps.auth1',
    'apps.wf',
    'apps.ops'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['dist'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# WSGI
WSGI_APPLICATION = 'server.wsgi.application'

# ASGI
ASGI_APPLICATION = 'server.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
            "capacity": 1500,
            "expiry": 10
        },
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = conf.DATABASES

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'dist/static')
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'dist/static'),
# )

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 人脸库配置
# 如果地址不存在，则自动创建/现在直接存库可不用
FACE_PATH = os.path.join(BASE_DIR, 'media/face')
if not os.path.exists(FACE_PATH):
    os.makedirs(FACE_PATH)


# 邮箱配置
EMAIL_HOST = conf.EMAIL_HOST
EMAIL_PORT = conf.EMAIL_PORT
EMAIL_HOST_USER = conf.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = conf.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = conf.EMAIL_USE_TLS

# 默认主键
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# 雪花ID生成配置
SNOW_DATACENTER_ID = conf.SNOW_DATACENTER_ID

# restframework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'apps.utils.permission.RbacPermission'
    ],
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'apps.utils.response.FitJSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer'
    # ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.MyPagination',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATETIME_INPUT_FORMATS': ['iso-8601', '%Y-%m-%d %H:%M:%S'],
    'DATE_FORMAT': '%Y-%m-%d',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 'UNAUTHENTICATED_USER': None,
    # 'UNAUTHENTICATED_TOKEN': None,
    'EXCEPTION_HANDLER': 'apps.utils.exceptions.custom_exception_hander',
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/second',
        'user': '200/second'
    }
}
# simplejwt配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

# 跨域配置/可用nginx处理,无需引入corsheaders
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Auth配置
AUTH_USER_MODEL = 'system.User'
AUTHENTICATION_BACKENDS = (
    'apps.auth1.authentication.CustomBackend',
)

# 缓存配置,有需要可更改为redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# celery配置,celery正常运行必须安装redis
CELERY_BROKER_URL = "redis://127.0.0.1:6379/3"   # 任务存储
CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker最多执行100个任务就会被销毁，可防止内存泄露
CELERY_TIMEZONE = 'Asia/Shanghai'  # 设置时区
CELERY_ENABLE_UTC = True  # 启动时区设置
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_EXTENDED = True
CELERY_TASK_TRACK_STARTED = True
CELERYD_SOFT_TIME_LIMIT = 60*10


# swagger配置
SWAGGER_SETTINGS = {
    'LOGIN_URL': '/django/admin/login/',
    'LOGOUT_URL': '/django/admin/logout/',
}

# 日志配置
# 创建日志的路径
LOG_PATH = os.path.join(BASE_DIR, 'log')
# 如果地址不存在，则自动创建log文件夹
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 日志格式
        'standard': {
            'format': '[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] '
                      '[%(levelname)s]- %(message)s'},
        'simple': {  # 简单格式
            'format': '%(levelname)s %(message)s'
        },
    },
    # 过滤
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # 定义具体处理日志的方式
    'handlers': {
        # 默认记录所有日志
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'all-{}.log'.format(datetime.now().strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 2,  # 文件大小
            'backupCount': 10,  # 备份数
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',  # 设置默认编码，否则打印出来汉字乱码
        },
        # 输出错误日志
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'error-{}.log'.format(datetime.now().strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 2,  # 文件大小
            'backupCount': 10,  # 备份数
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',  # 设置默认编码
        },
        # 控制台输出
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'standard'
        },
        # 输出info日志
        'info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'info-{}.log'.format(datetime.now().strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 2,
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',  # 设置默认编码
        },
    },
    # 配置用哪几种 handlers 来处理日志
    'loggers': {
        # 类型 为 django 处理所有类型的日志， 默认调用
        'django': {
            'handlers': ['default', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        # log 调用时需要当作参数传入
        'log': {
            'handlers': ['error', 'info', 'console', 'default'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# 项目
BASE_URL = conf.BASE_URL
BASE_URL_IN = conf.BASE_URL_IN
BASE_URL_OUT = conf.BASE_URL_OUT


# 运维相关
SD_PWD = conf.SD_PWD
BACKUP_PATH = conf.BACKUP_PATH
SH_PATH = conf.SH_PATH


# 百度语音
BD_SP_ID = conf.BD_SP_ID
BD_SP_KEY = conf.BD_SP_KEY
BD_SP_SECRET = conf.BD_SP_SECRET


# 微信有关
WXMP_ENABLED = conf.WXMP_ENABLED
WXMP_APPID = conf.WXMP_APPID
WXMP_APPSECRET = conf.WXMP_APPSECRET

WX_ENABLED = conf.WX_ENABLED
WX_APPID = conf.WX_APPID
WX_APPSECRET = conf.WX_APPSECRET