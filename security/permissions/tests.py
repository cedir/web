import mock

from django.test import TestCase
from security.permissions import IsAuthenticatedOrOptions


class IsAuthenticatedOrOptionsUnitTests(TestCase):
    def setUp(self):
        self.request = mock.Mock()
        self.view = mock.Mock()

    def test_has_permission(self):
        # Everyone can access OPTIONS
        self.request.method = 'OPTIONS'
        self.assertTrue(IsAuthenticatedOrOptions().has_permission(self.request, self.view))

        # Request has no user - has_permission = False
        self.request.user = None
        self.request.method = 'NOT_OPTIONS'
        self.assertFalse(IsAuthenticatedOrOptions().has_permission(self.request, self.view))

        # user.is_superuser = False - has_permission = False
        self.request.user = mock.Mock()
        self.request.user.is_authenticated.return_value = False
        self.assertFalse(IsAuthenticatedOrOptions().has_permission(self.request, self.view))

        # user.is_superuser = True - has_permission = True
        self.request.user.is_authenticated.return_value = True
        self.assertTrue(IsAuthenticatedOrOptions().has_permission(self.request, self.view))

