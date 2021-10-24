from time import sleep
from datetime import timedelta
from unittest import skipIf
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

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


class TestAutoLogoutSessionTime(TestAutoLogout):
    def _logout_session_time(self):
        self.assertLoginRequiredRedirect()

        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()

        sleep(1)
        self.assertLoginRequiredRedirect()

    def test_logout_session_time(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': 1}
        settings.USE_TZ = False
        self._logout_session_time()

    def test_logout_session_time_using_tz_utc(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': 1}
        settings.USE_TZ = True
        self._logout_session_time()

    def test_logout_session_time_using_tz_non_utc(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': 1}
        settings.USE_TZ = True
        settings.TIME_ZONE = 'Asia/Yekaterinburg'
        self._logout_session_time()

    def test_logout_session_time_timedelta(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': timedelta(seconds=1)}
        settings.USE_TZ = False
        self._logout_session_time()

    def test_logout_session_time_using_tz_utc_timedelta(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': timedelta(seconds=1)}
        settings.USE_TZ = True
        self._logout_session_time()

    def test_logout_session_time_using_tz_non_utc_timedelta(self):
        settings.AUTO_LOGOUT = {'SESSION_TIME': timedelta(seconds=1)}
        settings.USE_TZ = True
        settings.TIME_ZONE = 'Asia/Yekaterinburg'
        self._logout_session_time()

    def test_session_time_wrong_type(self):
        settings.AUTO_LOGOUT = {
            'IDLE_TIME': 1,
            'SESSION_TIME': '2',
        }

        self.client.force_login(self.user)

        exc_message = "AUTO_LOGOUT['SESSION_TIME'] should be `int` or `timedelta`, not `str`."
        with self.assertRaisesMessage(TypeError, exc_message):
            self.client.get(self.url)


class TestAutoLogoutIdleTime(TestAutoLogout):
    def _test_logout_idle_time_no_idle(self):
        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()

        for _ in range(10):
            sleep(0.5)
            self.assertLoginRequiredIsOk()

    def test_logout_idle_time_no_idle(self):
        settings.AUTO_LOGOUT = {'IDLE_TIME': 1}
        self._test_logout_idle_time_no_idle()

    def test_logout_idle_time_no_idle_timedelta(self):
        settings.AUTO_LOGOUT = {'IDLE_TIME': timedelta(seconds=1)}
        self._test_logout_idle_time_no_idle()

    def _test_logout_idle_time(self):
        self.client.force_login(self.user)
        self.assertLoginRequiredIsOk()

        sleep(1.5)
        self.assertLoginRequiredRedirect()

    def test_logout_idle_time(self):
        settings.AUTO_LOGOUT = {'IDLE_TIME': 1}
        self._test_logout_idle_time()

    def test_logout_idle_time_timedelta(self):
        settings.AUTO_LOGOUT = {'IDLE_TIME': timedelta(seconds=1)}
        self._test_logout_idle_time()

    def test_idle_time_wrong_type(self):
        settings.AUTO_LOGOUT = {
            'IDLE_TIME': '1',
            'SESSION_TIME': 2,
        }

        self.client.force_login(self.user)

        exc_message = "AUTO_LOGOUT['IDLE_TIME'] should be `int` or `timedelta`, not `str`."
        with self.assertRaisesMessage(TypeError, exc_message):
            self.client.get(self.url)


class TestAutoLogoutCombineConfigs(TestAutoLogout):
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


class TestAutoLogoutMessage(TestAutoLogout):
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


try:
    from selenium.webdriver.firefox.webdriver import WebDriver
    from selenium.webdriver.common.by import By
except ImportError:
    skip_selenium = True
else:
    skip_selenium = False


@skipIf(skip_selenium, 'No selenium')
class TestBrowser(StaticLiveServerTestCase):
    browser: WebDriver
    url = '/login-required/'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = WebDriver()
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.user = UserModel.objects.create_user('user', 'user@localhost', 'pass')
        self.superuser = UserModel.objects.create_superuser('superuser', 'superuser@localhost', 'pass')

    def _login_user(self):
        self.browser.get(f'{self.live_server_url}{settings.LOGIN_URL}')
        username_input = self.browser.find_element(By.CSS_SELECTOR, "input[name=username]")
        username_input.send_keys('user')
        password_input = self.browser.find_element(By.CSS_SELECTOR, "input[name=password]")
        password_input.send_keys('pass')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()

    def test_can_open_browser(self):
        self.browser.get(f'{self.live_server_url}{settings.LOGIN_URL}')
        self.assertIn('login page', self.browser.title)

    def test_auto_logout_session_time(self):
        settings.AUTO_LOGOUT['SESSION_TIME'] = 1
        self._login_user()
        sleep(0.5)
        self.assertIn('login required page', self.browser.title)
        sleep(0.5)
        self.browser.get(f'{self.live_server_url}{self.url}')
        self.assertIn('login page', self.browser.title)
