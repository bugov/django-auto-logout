#!/usr/bin/env python
import sys
import os

from django.core.management import execute_from_command_line

sys.path.append('example')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
execute_from_command_line(['runtests.py', 'test', 'example'])
