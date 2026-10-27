import runpy
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.settings import api_settings

from server import conf


class SigningKeyTests(SimpleTestCase):
    def test_missing_keys_show_configuration_error(self):
        for name in ('SECRET_KEY', 'JWT_SIGNING_KEY'):
            with self.subTest(name=name), patch.object(conf, name):
                delattr(conf, name)
                with self.assertRaisesMessage(ImproperlyConfigured, 'conf.py'):
                    runpy.run_path(str(Path(conf.__file__).with_name('settings.py')), run_name='server._settings_test')

    def test_empty_keys_fail(self):
        for django_key, jwt_key in (('', ''), ('django-test-' * 8, ''), ('', 'jwt-test-' * 8)):
            with self.subTest(django_key=django_key, jwt_key=jwt_key):
                with patch.multiple(conf, SECRET_KEY=django_key, JWT_SIGNING_KEY=jwt_key):
                    with self.assertRaises(ImproperlyConfigured):
                        runpy.run_path(str(Path(conf.__file__).with_name('settings.py')), run_name='server._settings_test')

    def test_keys_must_be_independent(self):
        with patch.multiple(conf, SECRET_KEY='same-test-' * 8, JWT_SIGNING_KEY='same-test-' * 8):
            with self.assertRaises(ImproperlyConfigured):
                runpy.run_path(str(Path(conf.__file__).with_name('settings.py')), run_name='server._settings_test')

    def test_keys_are_loaded_from_conf(self):
        with patch.multiple(conf, SECRET_KEY='django-test-' * 8, JWT_SIGNING_KEY='jwt-test-' * 8):
            loaded = runpy.run_path(str(Path(conf.__file__).with_name('settings.py')), run_name='server._settings_test')
            self.assertEqual(loaded['SECRET_KEY'], 'django-test-' * 8)
            self.assertEqual(loaded['SIMPLE_JWT']['SIGNING_KEY'], 'jwt-test-' * 8)

    def test_jwt_rejects_tokens_signed_with_django_key(self):
        self.assertNotEqual(api_settings.SIGNING_KEY, settings.SECRET_KEY)
        verifier = TokenBackend('HS256', signing_key=api_settings.SIGNING_KEY)
        wrong_signer = TokenBackend('HS256', signing_key=settings.SECRET_KEY)
        with self.assertRaises(TokenBackendError):
            verifier.decode(wrong_signer.encode({'user_id': 1}))
        self.assertEqual(verifier.decode(verifier.encode({'user_id': 1}))['user_id'], 1)
