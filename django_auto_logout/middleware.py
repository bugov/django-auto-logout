from datetime import datetime, timedelta
import logging
from typing import Callable, Optional
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model, logout
from django.contrib.messages import info
from pytz import timezone

LOGOUT_URL = settings.AUTO_LOGOUT.get('LOGOUT_URL', '/djal-send-logout/')
UserModel = get_user_model()
logger = logging.getLogger(__name__)


def _auto_logout(request: HttpRequest, options) -> Optional[HttpResponse]:
    user = request.user
    should_logout = False
    replace_response: Optional[HttpResponse] = None

    if settings.USE_TZ:
        now = datetime.now(tz=timezone(settings.TIME_ZONE))
    else:
        now = datetime.now()

    if settings.AUTO_LOGOUT.get('LOGOUT_ON_TABS_CLOSED'):
        if request.path == LOGOUT_URL and request.method.lower() == 'post':
            should_logout |= True
            replace_response = HttpResponse()
            logger.info('Client %r requested for logout', user)

    if options.get('SESSION_TIME') is not None:
        if isinstance(options['SESSION_TIME'], timedelta):
            ttl = options['SESSION_TIME']
        elif isinstance(options['SESSION_TIME'], int):
            ttl = timedelta(seconds=options['SESSION_TIME'])
        else:
            raise TypeError(f"AUTO_LOGOUT['SESSION_TIME'] should be `int` or `timedelta`, "
                            f"not `{type(options['SESSION_TIME']).__name__}`.")

        time_expired = user.last_login < now - ttl
        should_logout |= time_expired
        logger.debug('Check SESSION_TIME: %s < %s (%s)', user.last_login, now, time_expired)

    if options.get('IDLE_TIME') is not None:
        if isinstance(options['IDLE_TIME'], timedelta):
            ttl = options['IDLE_TIME']
        elif isinstance(options['IDLE_TIME'], int):
            ttl = timedelta(seconds=options['IDLE_TIME'])
        else:
            raise TypeError(f"AUTO_LOGOUT['IDLE_TIME'] should be `int` or `timedelta`, "
                            f"not `{type(options['IDLE_TIME']).__name__}`.")

        if 'django_auto_logout_last_request' in request.session:
            last_req = datetime.fromisoformat(request.session['django_auto_logout_last_request'])
        else:
            last_req = now
            request.session['django_auto_logout_last_request'] = last_req.isoformat()

        time_expired = last_req < now - ttl
        should_logout |= time_expired
        logger.debug('Check IDLE_TIME: %s < %s (%s)', last_req, now, time_expired)

        if should_logout:
            del request.session['django_auto_logout_last_request']
        else:
            request.session['django_auto_logout_last_request'] = now.isoformat()

    if should_logout:
        logger.debug('Logout user %s', user)
        logout(request)

        if options.get('MESSAGE') is not None:
            info(request, options['MESSAGE'])

    return replace_response


def auto_logout(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable:
    def middleware(request: HttpRequest) -> HttpResponse:
        if not request.user.is_anonymous and hasattr(settings, 'AUTO_LOGOUT'):
            replace_response = _auto_logout(request, settings.AUTO_LOGOUT)
            if replace_response:
                return replace_response

        return get_response(request)
    return middleware
