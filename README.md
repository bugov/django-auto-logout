# django-auto-logout

[![Build Status](https://app.travis-ci.com/bugov/django-auto-logout.svg?branch=master)](https://app.travis-ci.com/bugov/django-auto-logout)

Auto logout a user after specific time in Django.

Works with
- Python🐍 ≥ 3.7,
- Django🌐 ≥ 3.0.

**Documentation**
- [How to install](#installation)
- User logout in case of:
  - [downtime](#idle-time)
  - [session duration limitation](#session-time)
- [Auto-reload the browser page when the time runs out](#reload)
- [Add a message to inform the user about logging out](#message)

## <a name="installation"></a>✔️ Installation

```bash
pip install django-auto-logout
```

Append to `settings.py` middlewares:

```python
MIDDLEWARE = [
    # append after default middlewares
    'django_auto_logout.middleware.auto_logout',
]
```

---

**NOTE**

Make sure that the following middlewares are used before doing this:

- `django.contrib.sessions.middleware.SessionMiddleware`
- `django.contrib.auth.middleware.AuthenticationMiddleware`
- `django.contrib.messages.middleware.MessageMiddleware`

---

## <a name="idle-time"></a>💤 Logout in case of idle

Logout a user if there are no requests for a long time.

Add to `settings.py`:

```python
AUTO_LOGOUT = {'IDLE_TIME': 600}  # logout after 10 minutes of downtime
```

or the same, but with `datetime.timedelta` (more semantically):

```python
from datetime import timedelta

AUTO_LOGOUT = {'IDLE_TIME': timedelta(minutes=10)}
```

The user will log out the next time the page is requested.
See `REDIRECT_TO_LOGIN_IMMEDIATELY` to log out right after the idle-time has expired
(and redirect to login page).

### <a name="reload"></a>🔄 `REDIRECT_TO_LOGIN_IMMEDIATELY` after the idle-time has expired

Use the `REDIRECT_TO_LOGIN_IMMEDIATELY` option
if you want to redirect the user to the login page
immediately after the idle-time expires:

```python
from datetime import timedelta

AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=10),
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}
```

This requires a client-side script, so you should
modify your `context_processors` in `settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # ↓↓↓ Add this ↓↓↓
                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]
```

And add this to your templates (will add a redirect script to your html):

```
{{ redirect_to_login_immediately }}
```

If you want to use this in your JavaScript code, following template variables may be useful:

```
var sessionEnd = {{ seconds_until_session_end }};
var idleEnd = {{ seconds_until_idle_end }};
```

`REDIRECT_TO_LOGIN_IMMEDIATELY` works with `SESSION_TIME` too.

## <a name="session-time"></a>⌛ Limit session time

Logout a user after 3600 seconds (hour) from the last login.

Add to `settings.py`:

```python
AUTO_LOGOUT = {'SESSION_TIME': 3600}
```

or the same, but with `datetime.timedelta` (more semantically):

```python
from datetime import timedelta

AUTO_LOGOUT = {'SESSION_TIME': timedelta(hours=1)}
```

---

**NOTE**

See `REDIRECT_TO_LOGIN_IMMEDIATELY` option
if you want to redirect user to the login page
right after the idle-time has expired.

---

## <a name="message"></a>✉️ Show messages when logging out automatically

Set the message that will be displayed after the user automatically logs out of the system:

```python
AUTO_LOGOUT = {
    'SESSION_TIME': 3600,
    'MESSAGE': 'The session has expired. Please login again to continue.',
}
```

It uses `django.contrib.messages`. Don't forget to display messages in templates:

```html
{% for message in messages %}
    <div class="message {{ message.tags }}">
        {{ message }}
    </div>
{% endfor %}
```

---

**NOTE**

`messages` template variable provides by `django.contrib.messages.context_processors.messages`
context processor.

See `TEMPLATES` → `OPTIONS` → `context_processors` in your `settings.py` file.

---

## 🌈 Combine configurations

You can combine previous configurations. For example, you may want to logout a user
in case of downtime (5 minutes or more) and not allow working within one session
for more than half an hour:

```python
from datetime import timedelta

AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=5),
    'SESSION_TIME': timedelta(minutes=30),
    'MESSAGE': 'The session has expired. Please login again to continue.',
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}
```
