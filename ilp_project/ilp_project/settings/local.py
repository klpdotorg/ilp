from __future__ import absolute_import

from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ilp',
        'USER': 'ilp',
        'PASSWORD': 'ilp',
        'HOST': '127.0.0.1'
    }
}
