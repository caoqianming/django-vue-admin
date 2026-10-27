"""Isolated test database/cache; signing keys still come from conf.py."""
from .settings import *  # noqa: F403,F401

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
STATICFILES_DIRS = []
LOGGING = {'version': 1, 'disable_existing_loggers': False}
