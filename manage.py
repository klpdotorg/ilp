#!/usr/bin/env python
import os
import sys
import urllib.request

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ilp.settings")
    sys.path.append(os.path.join(os.getcwd(), 'apps'))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
