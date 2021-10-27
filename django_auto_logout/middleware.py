import logging
from typing import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model, logout
from django.contrib.messages import info

from .utils import now, seconds_until_idle_time_end, seconds_until_session_end

UserModel = get_user_model()
logger = logging.getLogger(__name__)


def _auto_logout(request: HttpRequest, options):
    should_logout = False
    current_time = now()

    if 'SESSION_TIME' in options:
        session_time = seconds_until_session_end(request, options['SESSION_TIME'], current_time)
        should_logout |= session_time < 0
        logger.debug('Check SESSION_TIME: %ss until session ends.', session_time)

    if 'IDLE_TIME' in options:
        idle_time = seconds_until_idle_time_end(request, options['IDLE_TIME'], current_time)
        should_logout |= idle_time < 0
        logger.debug('Check IDLE_TIME: %ss until idle ends.', idle_time)

        if should_logout and 'django_auto_logout_last_request' in request.session:
            del request.session['django_auto_logout_last_request']
        else:
            request.session['django_auto_logout_last_request'] = current_time.isoformat()

    if should_logout:
        logger.debug('Logout user %s', request.user)
        logout(request)

        if 'MESSAGE' in options:
            info(request, options['MESSAGE'])


def auto_logout(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable:
    def middleware(request: HttpRequest) -> HttpResponse:
        if not request.user.is_anonymous and hasattr(settings, 'AUTO_LOGOUT'):
            _auto_logout(request, settings.AUTO_LOGOUT)

        return get_response(request)
    return middleware
