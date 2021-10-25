from django.conf import settings
from django.utils.safestring import mark_safe

LOGOUT_URL = settings.AUTO_LOGOUT.get('LOGOUT_URL', '/djal-send-logout/')


def trim(s: str) -> str:
    return ''.join([line.strip() for line in s.split('\n')])


class LogoutOnTabClosed:
    template = trim(f'''
        <script>
            function djalSendLogout() {{
                var xhr = new XMLHttpRequest();
                xhr.open("POST", '{ LOGOUT_URL }', true);
                xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhr.send("");
            }}
            window.onbeforeunload = djalSendLogout;
        </script>
    ''')

    def __init__(self, request):
        self._request = request

    def __str__(self):
        return mark_safe(self.template)


def auto_logout_client(request):
    if settings.AUTO_LOGOUT.get('LOGOUT_ON_TABS_CLOSED'):
        html = LogoutOnTabClosed(request)
    else:
        html = ''

    return {
        'logout_on_tabs_closed': html
    }
