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
        return resp

    def assertLoginRequiredRedirect(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302, msg='Redirect for anonymous')
        self.assertEqual(resp['location'], f'{settings.LOGIN_URL}?next={self.url}')
        return resp

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

    def test_message_on_auto_logout(self):
        settings.AUTO_LOGOUT = {
            'SESSION_TIME': 1,
            'MESSAGE': 'The session has expired. Please login again to continue.',
        }
        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()
        sleep(1)
        resp = self.assertLoginRequiredRedirect()

        # display message after redirect
        resp = self.client.get(resp['location'])
        self.assertContains(resp, 'login page', msg_prefix=resp.content.decode())
        self.assertContains(resp, 'class="message info"', msg_prefix=resp.content.decode())
        self.assertContains(resp, settings.AUTO_LOGOUT['MESSAGE'])

        # message displays only once
        resp = self.assertLoginRequiredRedirect()
        resp = self.client.get(resp['location'])
        self.assertContains(resp, 'login page', msg_prefix=resp.content.decode())
        self.assertNotContains(resp, 'class="message info"', msg_prefix=resp.content.decode())

    def test_no_messages_if_no_messages(self):
        settings.AUTO_LOGOUT = {
            'SESSION_TIME': 1,
            'MESSAGE': None,
        }
        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()
        sleep(1)
        resp = self.assertLoginRequiredRedirect()
        resp = self.client.get(resp['location'])
        self.assertContains(resp, 'login page', msg_prefix=resp.content.decode())
        self.assertNotContains(resp, 'class="message info"', msg_prefix=resp.content.decode())
