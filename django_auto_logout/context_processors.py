from django.conf import settings
from django.utils.safestring import mark_safe
from .utils import now, seconds_until_session_end, seconds_until_idle_time_end

LOGOUT_TIMEOUT_SCRIPT_PATTERN = """
<script>
    (function() {
        var w = window,
            s = w.localStorage,
        %s
        w.addEventListener('load', function() {
            s['djalLogoutAt'] = at;
            
            function upd() {
                if (s['djalLogoutAt'] > at) {
                    at = s['djalLogoutAt'];
                    setTimeout(upd, at - Date.now());
                }
                else {
                    delete s['djalLogoutAt'];
                    w.location.reload();
                }
            }
            
            setTimeout(upd, at - Date.now());
        });
    })();
</script>
"""


def _trim(s: str) -> str:
    return ''.join([line.strip() for line in s.split('\n')])


def auto_logout_client(request):
    if request.user.is_anonymous:
        return {}

    options = getattr(settings, 'AUTO_LOGOUT')
    if not options:
        return {}

    ctx = {}
    current_time = now()

    if 'SESSION_TIME' in options:
        ctx['seconds_until_session_end'] = seconds_until_session_end(request, options['SESSION_TIME'], current_time)

    if 'IDLE_TIME' in options:
        ctx['seconds_until_idle_end'] = seconds_until_idle_time_end(request, options['IDLE_TIME'], current_time)

    if options.get('REDIRECT_TO_LOGIN_IMMEDIATELY'):
        at = None

        if 'SESSION_TIME' in options and 'IDLE_TIME' in options:
            at = (
                f"at=Date.now()+Math.max(Math.min({ ctx['seconds_until_session_end'] },"
                f"{ ctx['seconds_until_idle_end'] }),0)*1000+999;"
            )
        elif 'SESSION_TIME' in options:
            at = f"at=Date.now()+Math.max({ ctx['seconds_until_session_end'] },0)*1000+999;"
        elif 'IDLE_TIME' in options:
            at = f"at=Date.now()+Math.max({ ctx['seconds_until_idle_end'] },0)*1000+999;"

        if at:
            ctx['redirect_to_login_immediately'] = mark_safe(_trim(LOGOUT_TIMEOUT_SCRIPT_PATTERN % at))

    return ctx
