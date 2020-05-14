from .settings import *
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '...',
        'USER': '...',
        'PASSWORD': '...',
        'HOST': '...',
        'PORT': '5432',
    }
}
