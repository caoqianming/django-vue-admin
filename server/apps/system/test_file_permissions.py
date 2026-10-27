from django.core.cache import cache
from rest_framework.test import APITestCase

from .models import File, User


class FileDeletionTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.owner = User.objects.create_user('owner')
        self.other = User.objects.create_user('other')
        self.admin = User.objects.create_user('admin', is_superuser=True)
        self.file = File.objects.create(name='attachment', file='tests/example.txt', create_by=self.owner)
        self.url = f'/api/file/{self.file.pk}/'

    def test_other_user_cannot_delete(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(self.url).json()['code'], 403)
        self.file.refresh_from_db()
        self.assertFalse(self.file.is_deleted)

    def test_owner_can_delete(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(self.url).json()['code'], 204)
        self.file.refresh_from_db()
        self.assertTrue(self.file.is_deleted)

    def test_superuser_can_delete(self):
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(self.url).json()['code'], 204)

    def test_anonymous_cannot_delete(self):
        self.assertEqual(self.client.delete(self.url).json()['code'], 401)
        self.assertTrue(File.objects.filter(pk=self.file.pk).exists())

    def test_ownerless_file_requires_superuser(self):
        self.file.create_by = None
        self.file.save()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(self.url).json()['code'], 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(self.url).json()['code'], 204)

    def test_shared_file_remains_readable(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.url).json()['code'], 200)
