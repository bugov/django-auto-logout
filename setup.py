#!/usr/bin/env python

import os
from setuptools import setup, find_packages

from django_auto_logout import __version__


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


requires = [
    'django',
]
tests_require = requires + [
    'coverage',
    'tox',
]

setup(
    name='django-auto-logout',
    version=__version__,
    author='Georgy Bazhukov',
    author_email='georgy.bazhukov@gmail.com',
    description='Auto logout a user after specific time in Django',
    long_description=read('README.rst'),
    url='https://github.com/bugov/django-auto-logout',
    packages=find_packages(),
    include_package_data=True,
    license="BSD",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    requires=requires,
    tests_require=tests_require,
)
