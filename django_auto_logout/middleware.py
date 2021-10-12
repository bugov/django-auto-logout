from datetime import datetime, timedelta
import logging
from typing import Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model, logout
from pytz import timezone

UserModel = get_user_model()
logger = logging.getLogger(__name__)


def _auto_logout(request: HttpRequest, options):
    user = request.user
    should_logout = False

    if settings.USE_TZ:
        now = datetime.now(tz=timezone(settings.TIME_ZONE))
    else:
        now = datetime.now()

    if 'SESSION_TIME' in options:
        ttl = options['SESSION_TIME']
        should_logout = user.last_login < now - timedelta(seconds=ttl)
        logger.debug('Check SESSION_TIME: %s < %s (%s)', user.last_login, now, should_logout)

    if should_logout:
        logger.debug('Logout user %s', user)
        logout(request)


def auto_logout(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable:
    def middleware(request: HttpRequest) -> HttpResponse:
        if not request.user.is_anonymous and hasattr(settings, 'AUTO_LOGOUT'):
            _auto_logout(request, settings.AUTO_LOGOUT)

        return get_response(request)
    return middleware
