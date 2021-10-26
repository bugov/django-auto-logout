# django-auto-logout

[![Build Status](https://app.travis-ci.com/bugov/django-auto-logout.svg?branch=master)](https://app.travis-ci.com/bugov/django-auto-logout)

Auto logout a user after specific time in Django.

Works with
- Python🐍 ≥ 3.7,
- Django🌐 ≥ 3.0.

## ✔️ Installation

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

## 💤 Logout in case of idle

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

## ⌛ Limit session time

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

## ✉️ Show messages when logging out automatically

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

## ✨ Logout a user when all his tabs are closed (experimental)

If all tabs are closed or if the browser is closed, actually...

Add to `AUTO_LOGOUT` settings:

```python
AUTO_LOGOUT['LOGOUT_ON_TABS_CLOSED'] = True
```

Also for this option you should add a context processor:

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

Add `logout_on_tabs_closed` variable to your template layout:

```
{{ logout_on_tabs_closed }}
```

It works for almost all browsers on 🖥️:

- IE ≥ 8
- Edge ≥ 12
- Firefox ≥ 3.5
- Chrome ≥ 4
- Safari ≥ 4
- Opera ≥ 11.5

And 📱 browsers:

- iOS Safari ≥ 3.2
- Android Browser ≥ 94
- Android Chrome ≥ 94
- Android Firefox ≥ 92
- Opera Mobile ≥ 12

## 🌈 Combine configurations

You can combine previous configurations. For example, you may want to logout a user
in case of downtime (5 minutes or more) and not allow working within one session
for more than half an hour:

```python
from datetime import timedelta

AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=5),
    'SESSION_TIME': timedelta(minutes=30),
    'LOGOUT_ON_TABS_CLOSED': True,
    'MESSAGE': 'The session has expired. Please login again to continue.',
}
```
