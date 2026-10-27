from django.core.cache import cache
from rest_framework.test import APITestCase

from .models import Organization, User


class OrganizationTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.client.force_authenticate(User.objects.create_user('admin', is_superuser=True))

    def test_create_root_then_child_then_clear_parent(self):
        response = self.client.post('/api/system/organization/', {'name': 'Root', 'parent': None}, format='json')
        self.assertEqual(response.json()['code'], 201)
        root = Organization.objects.get(name='Root')
        self.assertIsNone(root.parent_id)
        response = self.client.post('/api/system/organization/', {'name': 'Child', 'parent': root.pk}, format='json')
        self.assertEqual(response.json()['code'], 201)
        child = Organization.objects.get(name='Child')
        self.assertEqual(child.parent_id, root.pk)
        response = self.client.put(f'/api/system/organization/{child.pk}/',
                                   {'name': 'Child', 'parent': None}, format='json')
        self.assertEqual(response.json()['code'], 200)
        child.refresh_from_db()
        self.assertIsNone(child.parent_id)
