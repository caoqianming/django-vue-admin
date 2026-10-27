from django.core.cache import cache
from rest_framework.test import APITestCase

from .models import Permission, Role, User
from .permission import get_permission_list


class UserPrivilegeTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.editor = User.objects.create_user('editor')
        role = Role.objects.create(name='user editor')
        role.perms.add(Permission.objects.create(name='Edit user', method='user_update'))
        self.editor.roles.add(role)
        self.target = User.objects.create_user('target')
        self.admin = User.objects.create_user('admin', is_superuser=True)
        self.client.force_authenticate(self.editor)

    def update_user(self, user, **fields):
        return self.client.put(f'/api/system/user/{user.pk}/',
                               {'username': user.username, **fields}, format='json')

    def test_editor_cannot_promote_self_or_others(self):
        for target in (self.editor, self.target):
            with self.subTest(username=target.username):
                self.assertEqual(self.update_user(target, is_superuser=True).json()['code'], 400)
                target.refresh_from_db()
                self.assertFalse(target.is_superuser)

    def test_editor_cannot_modify_superuser(self):
        self.assertEqual(self.update_user(self.admin, is_active=False).json()['code'], 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_editor_can_edit_normal_profile(self):
        self.assertEqual(self.update_user(self.target, name='Updated').json()['code'], 200)
        self.target.refresh_from_db()
        self.assertEqual(self.target.name, 'Updated')

    def test_superuser_can_promote_and_demote_with_cache_refresh(self):
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.update_user(self.target, is_superuser=True).json()['code'], 200)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_superuser)
        self.assertEqual(get_permission_list(self.target), ['admin'])
        self.assertEqual(self.update_user(self.target, is_superuser=False).json()['code'], 200)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_superuser)
        self.assertNotIn('admin', cache.get('target__perms'))

    def test_partial_update_cannot_bypass_privilege_validation(self):
        response = self.client.patch(f'/api/system/user/{self.target.pk}/',
                                     {'is_superuser': True}, format='json')
        self.assertEqual(response.json()['code'], 403)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_superuser)

    def test_superuser_partial_update_uses_modify_serializer(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f'/api/system/user/{self.target.pk}/',
                                     {'is_superuser': True}, format='json')
        self.assertEqual(response.json()['code'], 200)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_superuser)
