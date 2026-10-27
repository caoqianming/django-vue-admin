"""Load deployment signing keys without a shared development fallback."""
import os

from django.core.exceptions import ImproperlyConfigured


def load_signing_keys():
    keys = []
    for name in ('DJANGO_SECRET_KEY', 'JWT_SIGNING_KEY'):
        value = os.environ.get(name, '')
        if len(value) < 50 or len(set(value)) < 5:
            raise ImproperlyConfigured(
                f'{name} must be set to a unique, randomly generated secret '
                'of at least 50 characters.'
            )
        keys.append(value)
    if keys[0] == keys[1]:
        raise ImproperlyConfigured('DJANGO_SECRET_KEY and JWT_SIGNING_KEY must differ.')
    return tuple(keys)
