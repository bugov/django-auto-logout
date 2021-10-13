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

    def assertLoginRequiredIsOk(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'login required view', msg_prefix='Fine with authorized')

    def assertLoginRequiredRedirect(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f'{settings.LOGIN_URL}?next={self.url}', msg_prefix='Redirect for anonymous')

    def _logout_session_time(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': 1}
        self.assertLoginRequiredRedirect()

        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()

        sleep(1)
        self.assertLoginRequiredRedirect()

    def test_logout_session_time(self):
        settings.USE_TZ = False
        self._logout_session_time()

    def test_logout_session_time_using_tz_utc(self):
        settings.USE_TZ = True
        self._logout_session_time()

    def test_logout_session_time_using_tz_non_utc(self):
        settings.USE_TZ = True
        settings.TIME_ZONE = 'Asia/Yekaterinburg'
        self._logout_session_time()

    def test_logout_idle_time_no_idle(self):
        settings.AUTO_LOGOUT = {'IDLE_TIME': 1}
        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()

        for _ in range(10):
            sleep(0.5)
            self.assertLoginRequiredIsOk()

    def test_logout_idle_time(self):
        settings.AUTO_LOGOUT = {'IDLE_TIME': 1}
        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()

        sleep(1.5)
        self.assertLoginRequiredRedirect()

    def test_combine_idle_and_session_time(self):
        settings.AUTO_LOGOUT = {
            'IDLE_TIME': 1,
            'SESSION_TIME': 2,
        }

        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()

        sleep(0.5)
        self.assertLoginRequiredIsOk()
        sleep(0.5)
        self.assertLoginRequiredIsOk()
        sleep(0.5)
        self.assertLoginRequiredIsOk()
        sleep(0.5)
        self.assertLoginRequiredRedirect()

    def test_combine_idle_and_session_time_but_session_less_than_idle(self):
        settings.AUTO_LOGOUT = {
            'IDLE_TIME': 2,
            'SESSION_TIME': 1,
        }

        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()
        sleep(0.5)
        self.assertLoginRequiredIsOk()
        sleep(0.5)
        self.assertLoginRequiredRedirect()

        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()
        sleep(0.5)
        self.assertLoginRequiredIsOk()
        sleep(0.5)
        self.assertLoginRequiredRedirect()

        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()
        sleep(1)
        self.assertLoginRequiredRedirect()
