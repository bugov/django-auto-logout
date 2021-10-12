from time import sleep
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class TestAutoLogout(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user('user', 'user@localhost', 'pass')
        self.superuser = UserModel.objects.create_superuser('superuser', 'superuser@localhost', 'pass')
        self.url = '/login-required/'

    def _logout_session_time(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': 1}
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f'{settings.LOGIN_URL}?next={self.url}', msg_prefix='Redirect for anonymous')

        self.client.force_login(self.user)
        resp = self.client.get(self.url)
        self.assertContains(resp, 'login required view', msg_prefix='Fine with authorized')

        sleep(1)
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f'{settings.LOGIN_URL}?next={self.url}', msg_prefix='Logout on session time expired')

    def test_logout_session_time(self):
        settings.USE_TZ = False
        self._logout_session_time()

    def test_logout_session_time_using_tz(self):
        settings.USE_TZ = True
        self._logout_session_time()
