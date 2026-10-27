import os
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.settings import api_settings

from server.secrets import load_signing_keys


class SigningKeyTests(SimpleTestCase):
    def test_missing_or_weak_keys_fail(self):
        for values in ({}, {'DJANGO_SECRET_KEY': 'short'},
                       {'DJANGO_SECRET_KEY': 'a' * 64},
                       {'DJANGO_SECRET_KEY': 'django-test-' * 8},
                       {'DJANGO_SECRET_KEY': 'django-test-' * 8, 'JWT_SIGNING_KEY': 'short'}):
            with self.subTest(values=values), patch.dict(os.environ, values, clear=True):
                with self.assertRaises(ImproperlyConfigured):
                    load_signing_keys()

    def test_keys_must_be_independent(self):
        with patch.dict(os.environ, {'DJANGO_SECRET_KEY': 'same-test-' * 8,
                                     'JWT_SIGNING_KEY': 'same-test-' * 8}):
            with self.assertRaises(ImproperlyConfigured):
                load_signing_keys()

    def test_valid_keys_are_loaded(self):
        with patch.dict(os.environ, {'DJANGO_SECRET_KEY': 'django-test-' * 8,
                                     'JWT_SIGNING_KEY': 'jwt-test-' * 8}):
            self.assertEqual(load_signing_keys(), ('django-test-' * 8, 'jwt-test-' * 8))

    def test_jwt_rejects_tokens_signed_with_django_key(self):
        self.assertNotEqual(api_settings.SIGNING_KEY, settings.SECRET_KEY)
        verifier = TokenBackend('HS256', signing_key=api_settings.SIGNING_KEY)
        wrong_signer = TokenBackend('HS256', signing_key=settings.SECRET_KEY)
        with self.assertRaises(TokenBackendError):
            verifier.decode(wrong_signer.encode({'user_id': 1}))
        self.assertEqual(verifier.decode(verifier.encode({'user_id': 1}))['user_id'], 1)
