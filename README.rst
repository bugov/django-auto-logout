django-auto-logout
==================

.. image:: https://app.travis-ci.com/bugov/django-auto-logout.svg?branch=master
    :target: https://app.travis-ci.com/bugov/django-auto-logout

Auto logout a user after specific time in Django.

Works with Python ≥ 3.7, Django ≥ 3.0.

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

Logout in case of idle
----------------------

Logout a user if there are no requests for a long time.

Add to `settings`:

.. code:: python

    AUTO_LOGOUT = {'IDLE_TIME': 600}  # logout after 10 minutes of downtime


Limit session time
------------------

Logout a user after 3600 seconds (hour) from the last login.

Add to `settings`:

.. code:: python

    AUTO_LOGOUT = {'SESSION_TIME': 3600}

Combine configurations
----------------------

You can combine previous configurations. For example, you may want to logout a user
in case of downtime (5 minutes or more) and not allow working within one session
for more than half an hour:


.. code:: python

    AUTO_LOGOUT = {
        'IDLE_TIME': 300,  # 5 minutes
        'SESSION_TIME': 1800,  # 30 minutes
    }
