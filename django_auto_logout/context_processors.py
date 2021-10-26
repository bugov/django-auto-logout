from django.conf import settings
from django.utils.safestring import mark_safe

LOGOUT_URL = settings.AUTO_LOGOUT.get('LOGOUT_URL', '/djal-send-logout/')


def trim(s: str) -> str:
    if settings.DEBUG:
        return s
    return ''.join([line.strip() for line in s.split('\n')])


class LogoutOnTabClosed:
    template = trim(f'''
        <script>
            (function() {{
                var w = window,
                    s = w.localStorage;
        
                function out() {{
                    var x = new XMLHttpRequest();
                    x.open("POST", '{ LOGOUT_URL }', true);
                    x.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                    x.send("");
                }}
        
                w.addEventListener('load', function() {{
                    s['djalTabCounter']=Number(s['djalTabCounter']||0)+1;
                }});
        
                var unload = w.onbeforeunload;
                w.onbeforeunload = function () {{
                    var c = Number(s['djalTabCounter']||0);
                    if (c > 1) s['djalTabCounter']=c-1;
                    else {{
                        s['djalTabCounter']=0;
                        out();
                    }}
                    unload();
                }};
            }})();
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
        'logout_on_tabs_closed': html,
        'logout_url': LOGOUT_URL,
    }
