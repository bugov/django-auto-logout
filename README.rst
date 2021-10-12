django-auto-logout
==================

.. figure:: https://travis-ci.org/bugov/django-auto-logout.svg?branch=master

Auto logout a user after specific time in Django.

Works with Python ≥ 3.5, Django ≥ 3.0.

Installation
------------

.. code:: bash

    pip install django-auto-logout


Append to `settings` middlewares:

.. code:: python

    MIDDLEWARE = (
    ...
        'django_auto_logout.middleware.auto_logout',
    )

Limit session time
------------------

Logout a user after 3600 seconds (hour) from the last login.

Add to `settings`:

.. code:: python

    AUTO_LOGOUT = {'SESSION_TIME': 3600}
