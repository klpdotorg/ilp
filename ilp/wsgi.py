"""
WSGI config for ilp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import sys,os

PROJECT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT,'apps'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ilp.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
