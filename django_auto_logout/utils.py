from datetime import datetime, timedelta
from typing import Union
from django.conf import settings
from django.http import HttpRequest
from pytz import timezone


def now() -> datetime:
    """
    Returns the current time with the Django project timezone.
    :return: datetime
    """
    if settings.USE_TZ:
        return datetime.now(tz=timezone(settings.TIME_ZONE))
    return datetime.now()


def seconds_until_session_end(
    request: HttpRequest,
    session_time: Union[int, timedelta],
    current_time: datetime
) -> float:
    """
    Get seconds until the end of the session.
    :param request: django.http.HttpRequest
    :param session_time: int - for seconds | timedelta
    :param current_time: datetime - use django_auto_logout.utils.now
    :return: float
    """
    if isinstance(session_time, timedelta):
        ttl = session_time
    elif isinstance(session_time, int):
        ttl = timedelta(seconds=session_time)
    else:
        raise TypeError(f"AUTO_LOGOUT['SESSION_TIME'] should be `int` or `timedelta`, "
                        f"not `{type(session_time).__name__}`.")

    return (request.user.last_login - current_time + ttl).total_seconds()


def seconds_until_idle_time_end(
    request: HttpRequest,
    idle_time: Union[int, timedelta],
    current_time: datetime
) -> float:
    """
    Get seconds until the end of downtime.
    :param request: django.http.HttpRequest
    :param idle_time: int - for seconds | timedelta
    :param current_time: datetime - use django_auto_logout.utils.now
    :return: float
    """
    if isinstance(idle_time, timedelta):
        ttl = idle_time
    elif isinstance(idle_time, int):
        ttl = timedelta(seconds=idle_time)
    else:
        raise TypeError(f"AUTO_LOGOUT['IDLE_TIME'] should be `int` or `timedelta`, "
                        f"not `{type(idle_time).__name__}`.")

    if 'django_auto_logout_last_request' in request.session:
        last_req = datetime.fromisoformat(request.session['django_auto_logout_last_request'])
    else:
        last_req = current_time

    return (last_req - current_time + ttl).total_seconds()
